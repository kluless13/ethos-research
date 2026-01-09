#!/usr/bin/env python3
"""
Step 3: Fetch Twitter relationship data for vouch pairs.

For each vouch pair (A vouched for B), check:
- Does A follow B?
- Does B follow A?
- Has A mentioned/replied to B?
- Has B mentioned/replied to A?

Output: data/raw/twitter_relationships.json
"""

import sys
import json
import time
import random
import argparse
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from twitter_client import TwitterClient


def load_vouch_pairs(vouches_file: Path) -> list[dict]:
    """Load vouch pairs with Twitter handles from vouches.json"""
    with open(vouches_file) as f:
        data = json.load(f)
    return data.get("twitter_pairs", [])


def main():
    parser = argparse.ArgumentParser(description="Fetch Twitter data for vouch pairs")
    parser.add_argument("--sample", type=int, default=None, 
                       help="Sample N random pairs (default: all)")
    parser.add_argument("--test", type=int, default=None,
                       help="Test mode: only process N pairs")
    parser.add_argument("--resume", action="store_true",
                       help="Resume from existing output file")
    args = parser.parse_args()
    
    data_dir = Path(__file__).parent.parent / "data"
    vouches_file = data_dir / "raw" / "vouches.json"
    output_file = data_dir / "raw" / "twitter_relationships.json"
    
    print("=" * 60)
    print("ETHOS RESEARCH: Fetching Twitter Relationships")
    print("=" * 60)
    
    # Load vouch pairs
    print(f"\n📂 Loading vouch pairs from {vouches_file}...")
    pairs = load_vouch_pairs(vouches_file)
    print(f"   Total pairs with Twitter handles: {len(pairs):,}")
    
    # Deduplicate by (voucher, vouchee) - some may have multiple vouches
    unique_pairs = {}
    for p in pairs:
        key = (p["author_twitter"], p["subject_twitter"])
        if key not in unique_pairs:
            unique_pairs[key] = p
    pairs = list(unique_pairs.values())
    print(f"   Unique pairs: {len(pairs):,}")
    
    # Sample if requested
    if args.sample:
        pairs = random.sample(pairs, min(args.sample, len(pairs)))
        print(f"   Sampled: {len(pairs):,} pairs")
    
    # Test mode
    if args.test:
        pairs = pairs[:args.test]
        print(f"   Test mode: {len(pairs)} pairs")
    
    # Resume logic
    existing_results = []
    processed_keys = set()
    if args.resume and output_file.exists():
        with open(output_file) as f:
            existing_data = json.load(f)
            existing_results = existing_data.get("results", [])
            for r in existing_results:
                processed_keys.add((r["voucher"], r["vouchee"]))
        print(f"   Resuming: {len(existing_results)} already processed")
        pairs = [p for p in pairs if (p["author_twitter"], p["subject_twitter"]) not in processed_keys]
        print(f"   Remaining: {len(pairs)} pairs")
    
    if not pairs:
        print("\n✅ Nothing to process!")
        return
    
    # Estimate cost
    # Per pair: ~4 API calls (2 follow checks + 2 interaction searches)
    # Follow check: 100 credits, Search: 15 credits
    # Total: ~230 credits per pair = ~$0.0023
    estimated_cost = len(pairs) * 0.0023
    print(f"\n💰 Estimated cost: ${estimated_cost:.2f}")
    print(f"   ({len(pairs)} pairs × ~$0.0023 per pair)")
    
    if not args.test:
        response = input("\nProceed? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    # Fetch data
    print(f"\n🔄 Fetching Twitter relationships...")
    
    results = existing_results.copy()
    errors = []
    
    with TwitterClient() as client:
        for i, pair in enumerate(pairs):
            voucher = pair["author_twitter"]
            vouchee = pair["subject_twitter"]
            
            try:
                result = client.analyze_vouch_pair(voucher, vouchee)
                result["author_profile_id"] = pair.get("author_profile_id")
                result["subject_profile_id"] = pair.get("subject_profile_id")
                result["author_score"] = pair.get("author_score", 0)
                result["subject_score"] = pair.get("subject_score", 0)
                results.append(result)
                
                # Progress
                if (i + 1) % 10 == 0 or (i + 1) == len(pairs):
                    pct = 100 * (i + 1) / len(pairs)
                    print(f"   [{i+1}/{len(pairs)}] ({pct:.1f}%) @{voucher} → @{vouchee}: score={result['authenticity_score']:.1f}")
                
                # Save periodically
                if (i + 1) % 50 == 0:
                    _save_results(output_file, results, errors)
                
            except Exception as e:
                errors.append({
                    "voucher": voucher,
                    "vouchee": vouchee,
                    "error": str(e)
                })
                print(f"   ❌ Error for @{voucher} → @{vouchee}: {e}")
            
            # Rate limiting
            time.sleep(0.3)
    
    # Final save
    _save_results(output_file, results, errors)
    
    # Summary stats
    print(f"\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if results:
        follow_rate = sum(1 for r in results if r["voucher_follows_vouchee"]) / len(results)
        mutual_rate = sum(1 for r in results if r["mutual_follow"]) / len(results)
        interaction_rate = sum(1 for r in results if r["any_interaction"]) / len(results)
        avg_score = sum(r["authenticity_score"] for r in results) / len(results)
        
        print(f"\n📊 Results ({len(results)} pairs analyzed):")
        print(f"   Voucher follows vouchee: {100*follow_rate:.1f}%")
        print(f"   Mutual follow: {100*mutual_rate:.1f}%")
        print(f"   Any interaction: {100*interaction_rate:.1f}%")
        print(f"   Average authenticity score: {avg_score:.2f}")
    
    if errors:
        print(f"\n⚠️  Errors: {len(errors)}")
    
    print(f"\n💾 Saved to: {output_file}")


def _save_results(output_file: Path, results: list, errors: list):
    """Save results to file."""
    output_data = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total_processed": len(results),
        "errors": len(errors),
        "results": results,
        "error_details": errors
    }
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)


if __name__ == "__main__":
    main()

