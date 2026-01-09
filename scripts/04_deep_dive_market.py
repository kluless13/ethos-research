#!/usr/bin/env python3
"""
Deep Dive: Single Market Analysis

Performs comprehensive Twitter analysis for ONE market subject.
Produces a case study with real findings, not just percentages.

Usage:
    python scripts/04_deep_dive_market.py serpinxbt
    python scripts/04_deep_dive_market.py serpinxbt --max-vouchers 50

Output: data/analysis/{username}_deep_dive.json
"""

import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from twitter_client import TwitterClient


# ─────────────────────────────────────────────────────────────────────────────
# Data Loading
# ─────────────────────────────────────────────────────────────────────────────

def load_vouchers_for_user(data_dir: Path, username: str) -> list[dict]:
    """Load all vouchers for a specific user from vouches.json"""
    with open(data_dir / "raw" / "vouches.json") as f:
        data = json.load(f)
    
    vouchers = []
    seen = set()
    
    for pair in data.get("twitter_pairs", []):
        if pair["subject_twitter"].lower() == username.lower():
            # Deduplicate by voucher handle
            voucher_handle = pair["author_twitter"].lower()
            if voucher_handle not in seen:
                seen.add(voucher_handle)
                vouchers.append(pair)
    
    return vouchers


def load_market_info(data_dir: Path, username: str) -> Optional[dict]:
    """Load market info for a user from markets.json"""
    with open(data_dir / "raw" / "markets.json") as f:
        data = json.load(f)
    
    for market in data.get("markets", []):
        user = market.get("user", {})
        if user.get("username", "").lower() == username.lower():
            return market
    
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Twitter Analysis
# ─────────────────────────────────────────────────────────────────────────────

def get_user_profile(client: TwitterClient, username: str) -> Optional[dict]:
    """Get Twitter profile info for a user."""
    try:
        result = client.get_user_info(username)
        return result.get("data", {})
    except Exception as e:
        print(f"    ⚠️  Could not get profile for @{username}: {e}")
        return None


def get_interaction_details(client: TwitterClient, from_user: str, to_user: str) -> dict:
    """
    Get detailed interaction data from one user to another.
    Returns count, recency, and sample tweets.
    """
    result = {
        "from": from_user,
        "to": to_user,
        "count": 0,
        "tweets": [],
        "most_recent": None,
        "oldest": None,
    }
    
    try:
        # Search for mentions and replies
        query = f"from:{from_user} (@{to_user} OR to:{to_user})"
        response = client._get("/twitter/tweet/advanced_search", {
            "query": query,
            "queryType": "Latest"
        })
        
        tweets = response.get("tweets", [])
        if not tweets:
            tweets = response.get("data", {}).get("tweets", [])
        
        result["count"] = len(tweets)
        result["tweets"] = tweets[:5]  # Keep top 5 for sample
        
        if tweets:
            # Parse dates to find most recent and oldest
            dates = []
            for t in tweets:
                created = t.get("createdAt") or t.get("created_at")
                if created:
                    dates.append(created)
            
            if dates:
                result["most_recent"] = max(dates)
                result["oldest"] = min(dates)
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def categorize_voucher(
    voucher_profile: Optional[dict],
    interactions_to_target: dict,
    interactions_from_target: dict,
    voucher_follows_target: Optional[bool],
    target_follows_voucher: Optional[bool],
    voucher_ethos_score: int
) -> dict:
    """
    Categorize a voucher based on relationship strength and credibility.
    """
    category = {
        "relationship_tier": "unknown",  # inner_circle, active, passive, weak, suspicious
        "flags": [],
        "credibility_score": 0.0,  # 0-1 based on voucher quality
        "relationship_score": 0.0,  # 0-1 based on Twitter relationship
    }
    
    # ─── Relationship scoring ───
    rel_score = 0.0
    
    # Interactions are the strongest signal
    to_count = interactions_to_target.get("count", 0)
    from_count = interactions_from_target.get("count", 0)
    total_interactions = to_count + from_count
    
    if total_interactions >= 10:
        rel_score += 0.5
        category["flags"].append("frequent_interactions")
    elif total_interactions >= 3:
        rel_score += 0.35
    elif total_interactions >= 1:
        rel_score += 0.2
    
    # Bidirectional interaction is very strong
    if to_count > 0 and from_count > 0:
        rel_score += 0.2
        category["flags"].append("bidirectional")
    
    # Follow relationship
    if voucher_follows_target:
        rel_score += 0.15
    if target_follows_voucher:
        rel_score += 0.15
        category["flags"].append("followed_back")
    
    category["relationship_score"] = min(rel_score, 1.0)
    
    # ─── Credibility scoring ───
    cred_score = 0.0
    
    if voucher_profile:
        followers = voucher_profile.get("followers", 0)
        following = voucher_profile.get("following", 0)
        created = voucher_profile.get("createdAt", "")
        
        # Follower count (log scale)
        if followers >= 10000:
            cred_score += 0.3
            category["flags"].append("high_followers")
        elif followers >= 1000:
            cred_score += 0.2
        elif followers >= 100:
            cred_score += 0.1
        elif followers < 50:
            category["flags"].append("low_followers")
        
        # Account age
        if created:
            try:
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - created_dt).days
                if age_days >= 365 * 2:
                    cred_score += 0.2
                elif age_days >= 365:
                    cred_score += 0.15
                elif age_days >= 180:
                    cred_score += 0.1
                elif age_days < 90:
                    category["flags"].append("new_account")
            except:
                pass
        
        # Follower/following ratio (detect bots)
        if following > 0:
            ratio = followers / following
            if ratio > 2:
                cred_score += 0.1
            elif ratio < 0.1 and followers < 100:
                category["flags"].append("suspicious_ratio")
        
        # Blue verified
        if voucher_profile.get("isBlueVerified"):
            cred_score += 0.1
            category["flags"].append("verified")
    
    # Ethos score
    if voucher_ethos_score >= 1500:
        cred_score += 0.2
        category["flags"].append("high_ethos")
    elif voucher_ethos_score >= 1000:
        cred_score += 0.1
    
    category["credibility_score"] = min(cred_score, 1.0)
    
    # ─── Determine tier ───
    rel = category["relationship_score"]
    cred = category["credibility_score"]
    
    if rel >= 0.7 and "bidirectional" in category["flags"]:
        category["relationship_tier"] = "inner_circle"
    elif rel >= 0.5:
        category["relationship_tier"] = "active"
    elif rel >= 0.2:
        category["relationship_tier"] = "passive"
    elif rel > 0:
        category["relationship_tier"] = "weak"
    else:
        category["relationship_tier"] = "none"
    
    # Check for suspicious patterns
    suspicious_flags = {"new_account", "low_followers", "suspicious_ratio"}
    if suspicious_flags & set(category["flags"]) and rel < 0.2:
        category["relationship_tier"] = "suspicious"
    
    return category


# ─────────────────────────────────────────────────────────────────────────────
# Main Analysis
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Deep dive analysis on a single market")
    parser.add_argument("username", help="Twitter username to analyze (the market subject)")
    parser.add_argument("--max-vouchers", type=int, default=None,
                       help="Limit number of vouchers to analyze (default: all)")
    parser.add_argument("--yes", "-y", action="store_true",
                       help="Skip confirmation prompt")
    args = parser.parse_args()
    
    username = args.username.lstrip("@").lower()
    
    data_dir = Path(__file__).parent.parent / "data"
    output_dir = data_dir / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{username}_deep_dive.json"
    
    print("=" * 70)
    print(f"DEEP DIVE: @{username}")
    print("=" * 70)
    
    # ─── Load data ───
    print(f"\n📂 Loading data...")
    
    vouchers = load_vouchers_for_user(data_dir, username)
    print(f"   Vouchers found: {len(vouchers)}")
    
    market_info = load_market_info(data_dir, username)
    if market_info:
        user = market_info.get("user", {})
        print(f"   Ethos score: {user.get('score', 'N/A')}")
        print(f"   Trust votes: {market_info.get('trustVotes', 0)}")
        print(f"   Distrust votes: {market_info.get('distrustVotes', 0)}")
    
    if not vouchers:
        print("❌ No vouchers found for this user!")
        return
    
    # Limit if requested
    if args.max_vouchers:
        vouchers = vouchers[:args.max_vouchers]
        print(f"   Limited to: {len(vouchers)} vouchers")
    
    # ─── Cost estimate ───
    # Per voucher: ~4 API calls (profile + 2 interaction searches + follow check)
    # Profile: 18 credits, Search: 15 credits each, Follow: ~15 credits
    # Total: ~63 credits = ~$0.00063 per voucher
    # Plus target profile and tweets: ~50 credits
    estimated_calls = len(vouchers) * 4 + 5
    estimated_cost = estimated_calls * 0.00015  # rough average
    
    print(f"\n💰 Estimated cost: ${estimated_cost:.3f}")
    print(f"   (~{estimated_calls} API calls)")
    
    if not args.yes:
        response = input("\nProceed? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    # ─── Analyze ───
    print(f"\n🔍 Starting deep dive analysis...")
    
    results = {
        "username": username,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "target_profile": None,
        "market_info": market_info,
        "voucher_count": len(vouchers),
        "vouchers_analyzed": [],
        "summary": {},
    }
    
    with TwitterClient() as client:
        # 1. Get target profile
        print(f"\n[1/3] Getting @{username}'s profile...")
        target_profile = get_user_profile(client, username)
        results["target_profile"] = target_profile
        
        if target_profile:
            print(f"   Followers: {target_profile.get('followers', 'N/A'):,}")
            print(f"   Following: {target_profile.get('following', 'N/A'):,}")
            print(f"   Created: {target_profile.get('createdAt', 'N/A')}")
        
        time.sleep(0.2)
        
        # 2. Analyze each voucher
        print(f"\n[2/3] Analyzing {len(vouchers)} vouchers...")
        
        tier_counts = defaultdict(int)
        
        for i, v in enumerate(vouchers):
            voucher_handle = v["author_twitter"]
            voucher_ethos = v.get("author_score", 0)
            
            voucher_result = {
                "handle": voucher_handle,
                "ethos_score": voucher_ethos,
                "profile": None,
                "interactions_to_target": None,
                "interactions_from_target": None,
                "voucher_follows_target": None,
                "target_follows_voucher": None,
                "category": None,
            }
            
            # Get voucher profile
            voucher_profile = get_user_profile(client, voucher_handle)
            voucher_result["profile"] = voucher_profile
            time.sleep(0.15)
            
            # Get interactions voucher → target
            interactions_to = get_interaction_details(client, voucher_handle, username)
            voucher_result["interactions_to_target"] = interactions_to
            time.sleep(0.15)
            
            # Get interactions target → voucher
            interactions_from = get_interaction_details(client, username, voucher_handle)
            voucher_result["interactions_from_target"] = interactions_from
            time.sleep(0.15)
            
            # Check follow relationships
            try:
                voucher_result["voucher_follows_target"] = client.check_follow_quick(voucher_handle, username)
            except:
                pass
            time.sleep(0.15)
            
            try:
                voucher_result["target_follows_voucher"] = client.check_follow_quick(username, voucher_handle)
            except:
                pass
            time.sleep(0.1)
            
            # Categorize
            category = categorize_voucher(
                voucher_profile,
                interactions_to,
                interactions_from,
                voucher_result["voucher_follows_target"],
                voucher_result["target_follows_voucher"],
                voucher_ethos
            )
            voucher_result["category"] = category
            tier_counts[category["relationship_tier"]] += 1
            
            results["vouchers_analyzed"].append(voucher_result)
            
            # Progress
            if (i + 1) % 10 == 0 or (i + 1) == len(vouchers):
                print(f"   [{i+1}/{len(vouchers)}] @{voucher_handle}: {category['relationship_tier']} "
                      f"(rel={category['relationship_score']:.2f}, cred={category['credibility_score']:.2f})")
            
            # Save periodically
            if (i + 1) % 25 == 0:
                _save_results(output_file, results)
        
        # 3. Generate summary
        print(f"\n[3/3] Generating summary...")
        
        analyzed = results["vouchers_analyzed"]
        
        results["summary"] = {
            "total_vouchers": len(analyzed),
            "tiers": dict(tier_counts),
            "tier_percentages": {k: round(v / len(analyzed) * 100, 1) for k, v in tier_counts.items()},
            "avg_relationship_score": round(sum(v["category"]["relationship_score"] for v in analyzed) / len(analyzed), 3),
            "avg_credibility_score": round(sum(v["category"]["credibility_score"] for v in analyzed) / len(analyzed), 3),
            "with_any_interaction": sum(1 for v in analyzed if v["interactions_to_target"]["count"] > 0),
            "with_bidirectional": sum(1 for v in analyzed if "bidirectional" in v["category"]["flags"]),
            "followed_back": sum(1 for v in analyzed if v["target_follows_voucher"]),
            "high_ethos_vouchers": sum(1 for v in analyzed if v["ethos_score"] >= 1500),
            "suspicious_count": tier_counts.get("suspicious", 0),
        }
        
        # Find notable vouchers
        inner_circle = [v for v in analyzed if v["category"]["relationship_tier"] == "inner_circle"]
        suspicious = [v for v in analyzed if v["category"]["relationship_tier"] == "suspicious"]
        
        results["summary"]["inner_circle"] = [
            {"handle": v["handle"], "interaction_count": v["interactions_to_target"]["count"] + v["interactions_from_target"]["count"]}
            for v in sorted(inner_circle, key=lambda x: -(x["interactions_to_target"]["count"] + x["interactions_from_target"]["count"]))[:10]
        ]
        
        results["summary"]["suspicious_accounts"] = [
            {"handle": v["handle"], "flags": v["category"]["flags"]}
            for v in suspicious[:10]
        ]
    
    # Save final
    _save_results(output_file, results)
    
    # ─── Print findings ───
    print(f"\n" + "=" * 70)
    print(f"FINDINGS: @{username}")
    print("=" * 70)
    
    s = results["summary"]
    
    print(f"\n📊 Voucher Tiers ({s['total_vouchers']} analyzed):")
    for tier in ["inner_circle", "active", "passive", "weak", "none", "suspicious"]:
        count = s["tiers"].get(tier, 0)
        pct = s["tier_percentages"].get(tier, 0)
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"   {tier:15} {bar} {count:3} ({pct:5.1f}%)")
    
    print(f"\n📈 Key Metrics:")
    print(f"   Any interaction with @{username}: {s['with_any_interaction']} ({100*s['with_any_interaction']/s['total_vouchers']:.1f}%)")
    print(f"   Bidirectional (both ways): {s['with_bidirectional']} ({100*s['with_bidirectional']/s['total_vouchers']:.1f}%)")
    print(f"   @{username} follows back: {s['followed_back']} ({100*s['followed_back']/s['total_vouchers']:.1f}%)")
    print(f"   Avg relationship score: {s['avg_relationship_score']:.2f}")
    print(f"   Avg credibility score: {s['avg_credibility_score']:.2f}")
    
    if s["inner_circle"]:
        print(f"\n⭐ Inner Circle (top relationships):")
        for v in s["inner_circle"][:5]:
            print(f"   @{v['handle']}: {v['interaction_count']} interactions")
    
    if s["suspicious_accounts"]:
        print(f"\n⚠️  Suspicious Vouchers:")
        for v in s["suspicious_accounts"][:5]:
            print(f"   @{v['handle']}: {', '.join(v['flags'])}")
    
    print(f"\n💾 Full results saved to: {output_file}")
    print(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")


def _save_results(output_file: Path, results: dict):
    """Save results to file."""
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)


if __name__ == "__main__":
    main()

