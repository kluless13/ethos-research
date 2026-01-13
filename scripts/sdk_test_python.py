#!/usr/bin/env python3
"""
SDK Test: Python (ethos-py)

Tests the official ethos-py SDK by replicating the functionality
from 01_fetch_markets.py and 02_fetch_vouches.py.

Usage:
    python scripts/sdk_test_python.py
"""

import json
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from ethos import Ethos


def test_profile_stats(client: Ethos):
    """Test getting profile stats."""
    print("\n📊 Testing Profile Stats...")
    try:
        stats = client.profiles.stats()
        print(f"   ✅ Active profiles: {stats.active_profiles:,}")
        print(f"   ✅ Invites available: {stats.invites_available:,}")
        return stats
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def test_markets(client: Ethos, max_markets: int = 50):
    """Test fetching markets."""
    print(f"\n🏪 Testing Markets (first {max_markets})...")
    
    markets = []
    try:
        for i, market in enumerate(client.markets.list()):
            markets.append(market)
            if i + 1 >= max_markets:
                break
        
        print(f"   ✅ Fetched {len(markets)} markets")
        
        # Show some stats
        with_activity = sum(1 for m in markets if m.trust_votes > 1 or m.distrust_votes > 1)
        print(f"   ✅ Markets with activity: {with_activity}")
        
        # Show top markets by volume
        top_5 = sorted(markets, key=lambda m: -(m.trust_votes + m.distrust_votes))[:5]
        print(f"\n   📈 Top 5 by votes:")
        for m in top_5:
            print(f"      Profile {m.profile_id}: trust={m.trust_votes}, distrust={m.distrust_votes}")
        
        return markets
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_top_markets(client: Ethos, markets: list):
    """Analyze top markets from already-fetched data."""
    print("\n🏆 Analyzing Top Markets...")
    
    if not markets:
        print("   ❌ No markets data to analyze")
        return {}
    
    try:
        # Sort by total votes
        top_by_votes = sorted(markets, key=lambda m: -(m.trust_votes + m.distrust_votes))[:5]
        print(f"   ✅ Top 5 by total votes:")
        for m in top_by_votes[:3]:
            print(f"      Profile {m.profile_id}: trust={m.trust_votes}, distrust={m.distrust_votes}")
        
        # Sort by trust percentage 
        trusted = sorted(markets, key=lambda m: -m.trust_price if m.trust_price else 0)[:5]
        print(f"   ✅ Most trusted (by price):")
        for m in trusted[:3]:
            print(f"      Profile {m.profile_id}: trust_price={m.trust_price:.2%}")
        
        return {"top_by_votes": top_by_votes, "most_trusted": trusted}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {}


def test_vouches(client: Ethos, max_vouches: int = 100):
    """Test fetching vouches."""
    print(f"\n🤝 Testing Vouches (first {max_vouches})...")
    
    vouches = []
    try:
        for i, vouch in enumerate(client.vouches.list()):
            vouches.append(vouch)
            if i + 1 >= max_vouches:
                break
        
        print(f"   ✅ Fetched {len(vouches)} vouches")
        
        # Count unique relationships
        # Note: SDK uses target_profile_id instead of subject_profile_id
        pairs = set()
        for v in vouches:
            pairs.add((v.author_profile_id, v.target_profile_id))
        print(f"   ✅ Unique vouch relationships: {len(pairs)}")
        
        # Top vouchers (by count in our sample)
        voucher_counts = defaultdict(int)
        for v in vouches:
            voucher_counts[v.author_profile_id] += 1
        
        top_vouchers = sorted(voucher_counts.items(), key=lambda x: -x[1])[:5]
        print(f"\n   📤 Top vouchers (in sample):")
        for profile_id, count in top_vouchers:
            print(f"      Profile {profile_id}: {count} vouches given")
        
        # Top vouchees
        vouchee_counts = defaultdict(int)
        for v in vouches:
            vouchee_counts[v.target_profile_id] += 1
        
        top_vouchees = sorted(vouchee_counts.items(), key=lambda x: -x[1])[:5]
        print(f"\n   📥 Most vouched (in sample):")
        for profile_id, count in top_vouchees:
            print(f"      Profile {profile_id}: {count} vouches received")
        
        return vouches
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_user_lookup(client: Ethos):
    """Test looking up a user by Twitter handle."""
    print("\n🔍 Testing User Lookup...")
    
    # Test known Ethos users (found in vouches data)
    test_handles = ["edoweb3", "serpinxbt", "crypsaf"]
    
    for handle in test_handles:
        try:
            user = client.users.get_by_twitter(handle)
            print(f"   ✅ @{handle}:")
            print(f"      ID: {user.id}")
            print(f"      Profile ID: {user.profile_id}")
            print(f"      Score: {user.score}")
            print(f"      XP: {user.xp_total:,}")
            print(f"      Vouches received: {user.stats.vouch.received.count}")
            return user
        except Exception as e:
            print(f"   ⚠️  @{handle} not found: {e}")
    
    return None


def test_vouch_lookup(client: Ethos, profile_id: int):
    """Test looking up vouches for a specific profile."""
    print(f"\n🔎 Testing Vouch Lookup for Profile {profile_id}...")
    
    try:
        # Vouches received
        received = client.vouches.for_profile(profile_id)
        print(f"   ✅ Vouches received: {len(received)}")
        
        # Vouches given
        given = client.vouches.by_profile(profile_id)
        print(f"   ✅ Vouches given: {len(given)}")
        
        return {"received": received, "given": given}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {}


def main():
    print("=" * 70)
    print("SDK TEST: ethos-py (Python)")
    print("=" * 70)
    print(f"Started at: {datetime.now().isoformat()}")
    
    # Initialize client
    print("\n🚀 Initializing Ethos client...")
    client = Ethos()
    print(f"   ✅ Client ready (base URL: {client.config.base_url})")
    
    # Run tests
    results = {}
    
    # 1. Profile stats
    results["stats"] = test_profile_stats(client)
    
    # 2. Markets
    results["markets"] = test_markets(client, max_markets=50)
    results["top_markets"] = test_top_markets(client, results["markets"])
    
    # 3. Vouches
    results["vouches"] = test_vouches(client, max_vouches=100)
    
    # 4. User lookup (using users resource, not profiles)
    user = test_user_lookup(client)
    if user:
        results["user_lookup"] = user
        # 5. Vouch lookup for that user's profile
        results["vouch_lookup"] = test_vouch_lookup(client, user.profile_id)
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    checks = [
        ("Profile Stats", results.get("stats") is not None),
        ("Markets Fetch", len(results.get("markets", [])) > 0),
        ("Top Markets", len(results.get("top_markets", {})) > 0),
        ("Vouches Fetch", len(results.get("vouches", [])) > 0),
        ("User Lookup", results.get("user_lookup") is not None),
    ]
    
    passed = sum(1 for _, ok in checks if ok)
    print(f"\n✅ Passed: {passed}/{len(checks)}")
    
    for name, ok in checks:
        status = "✅" if ok else "❌"
        print(f"   {status} {name}")
    
    # Close client
    client.close()
    print(f"\n🏁 Completed at: {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
