#!/usr/bin/env python3
"""
Step 3: Fetch Twitter data organized BY MARKET.

For each of the 219 market subjects:
1. Find all vouchers for that subject
2. Check Twitter relationships (voucher → subject)
3. Calculate per-market authenticity metrics

Output: data/raw/market_authenticity.json
"""

import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from twitter_client import TwitterClient


def load_data(data_dir: Path) -> tuple[list, dict]:
    """Load markets and vouches, return markets and vouches grouped by subject."""
    
    # Load markets
    with open(data_dir / "raw" / "markets.json") as f:
        markets_data = json.load(f)
    markets = markets_data["markets"]
    
    # Load vouches
    with open(data_dir / "raw" / "vouches.json") as f:
        vouches_data = json.load(f)
    
    # Group vouches by subject (vouchee)
    vouches_by_subject = defaultdict(list)
    for pair in vouches_data.get("twitter_pairs", []):
        subject = pair["subject_twitter"]
        vouches_by_subject[subject].append(pair)
    
    return markets, vouches_by_subject


def main():
    parser = argparse.ArgumentParser(description="Fetch Twitter data by market")
    parser.add_argument("--markets", type=int, default=None,
                       help="Limit to N markets (default: all 219)")
    parser.add_argument("--vouchers-per-market", type=int, default=20,
                       help="Max vouchers to check per market (default: 20)")
    parser.add_argument("--resume", action="store_true",
                       help="Resume from existing output")
    parser.add_argument("--yes", "-y", action="store_true",
                       help="Skip confirmation prompt")
    args = parser.parse_args()
    
    data_dir = Path(__file__).parent.parent / "data"
    output_file = data_dir / "raw" / "market_authenticity.json"
    
    print("=" * 60)
    print("ETHOS RESEARCH: Twitter Analysis by Market")
    print("=" * 60)
    
    # Load data
    print(f"\n📂 Loading data...")
    markets, vouches_by_subject = load_data(data_dir)
    print(f"   Markets: {len(markets)}")
    print(f"   Subjects with vouches: {len(vouches_by_subject)}")
    
    # Filter markets with vouches
    markets_with_vouches = []
    for m in markets:
        username = m.get("user", {}).get("username")
        if username and username in vouches_by_subject:
            markets_with_vouches.append({
                "market": m,
                "username": username,
                "vouchers": vouches_by_subject[username]
            })
    
    print(f"   Markets with vouches: {len(markets_with_vouches)}")
    
    # Sort by number of vouchers (most vouched first)
    markets_with_vouches.sort(key=lambda x: -len(x["vouchers"]))
    
    # Limit markets if requested
    if args.markets:
        markets_with_vouches = markets_with_vouches[:args.markets]
        print(f"   Limited to: {len(markets_with_vouches)} markets")
    
    # Resume logic
    existing_results = {}
    if args.resume and output_file.exists():
        with open(output_file) as f:
            existing_data = json.load(f)
            for r in existing_data.get("markets", []):
                existing_results[r["username"]] = r
        print(f"   Resuming: {len(existing_results)} markets already done")
    
    # Calculate total vouchers to check
    total_vouchers = sum(
        min(len(m["vouchers"]), args.vouchers_per_market) 
        for m in markets_with_vouches 
        if m["username"] not in existing_results
    )
    
    # Cost estimate: ~60 credits per pair = ~$0.0006
    estimated_cost = total_vouchers * 0.0006
    print(f"\n💰 Estimated cost: ${estimated_cost:.2f}")
    print(f"   ({total_vouchers} voucher pairs to check)")
    
    if total_vouchers == 0:
        print("\n✅ Nothing to process!")
        return
    
    if not args.yes:
        response = input("\nProceed? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    # Process each market
    print(f"\n🔄 Processing markets...")
    
    results = list(existing_results.values())
    
    with TwitterClient() as client:
        for i, mdata in enumerate(markets_with_vouches):
            username = mdata["username"]
            
            # Skip if already done
            if username in existing_results:
                continue
            
            market = mdata["market"]
            vouchers = mdata["vouchers"][:args.vouchers_per_market]
            
            print(f"\n[{i+1}/{len(markets_with_vouches)}] @{username} ({len(vouchers)} vouchers)")
            
            market_result = {
                "username": username,
                "profile_id": market.get("user", {}).get("profileId"),
                "ethos_score": market.get("user", {}).get("score", 0),
                "trust_votes": market.get("trustVotes", 0),
                "distrust_votes": market.get("distrustVotes", 0),
                "total_vouchers_checked": len(vouchers),
                "voucher_results": [],
                "stats": {}
            }
            
            # Check each voucher
            for j, v in enumerate(vouchers):
                voucher = v["author_twitter"]
                
                try:
                    pair_result = client.analyze_vouch_pair(voucher, username)
                    pair_result["voucher_ethos_score"] = v.get("author_score", 0)
                    market_result["voucher_results"].append(pair_result)
                    
                    if (j + 1) % 5 == 0:
                        print(f"   Checked {j+1}/{len(vouchers)} vouchers...")
                    
                except Exception as e:
                    print(f"   ❌ Error @{voucher}: {e}")
                
                time.sleep(0.2)
            
            # Calculate market stats
            vr = market_result["voucher_results"]
            if vr:
                market_result["stats"] = {
                    "follow_rate": sum(1 for r in vr if r.get("voucher_follows_vouchee")) / len(vr),
                    "mutual_follow_rate": sum(1 for r in vr if r.get("mutual_follow")) / len(vr),
                    "interaction_rate": sum(1 for r in vr if r.get("any_interaction")) / len(vr),
                    "avg_authenticity": sum(r.get("authenticity_score", 0) for r in vr) / len(vr)
                }
                print(f"   → Interaction rate: {100*market_result['stats']['interaction_rate']:.0f}%, "
                      f"Avg score: {market_result['stats']['avg_authenticity']:.2f}")
            
            results.append(market_result)
            
            # Save periodically
            if (i + 1) % 5 == 0:
                _save_results(output_file, results)
    
    # Final save
    _save_results(output_file, results)
    
    # Summary
    print(f"\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_stats = [m["stats"] for m in results if m.get("stats")]
    if all_stats:
        avg_follow = sum(s["follow_rate"] for s in all_stats) / len(all_stats)
        avg_mutual = sum(s["mutual_follow_rate"] for s in all_stats) / len(all_stats)
        avg_interaction = sum(s["interaction_rate"] for s in all_stats) / len(all_stats)
        avg_auth = sum(s["avg_authenticity"] for s in all_stats) / len(all_stats)
        
        print(f"\n📊 Across {len(all_stats)} markets:")
        print(f"   Avg follow rate: {100*avg_follow:.1f}%")
        print(f"   Avg mutual follow: {100*avg_mutual:.1f}%")
        print(f"   Avg interaction rate: {100*avg_interaction:.1f}%")
        print(f"   Avg authenticity score: {avg_auth:.2f}")
    
    print(f"\n💾 Saved to: {output_file}")


def _save_results(output_file: Path, results: list):
    """Save results to file."""
    output_data = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total_markets": len(results),
        "markets": results
    }
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)


if __name__ == "__main__":
    main()

