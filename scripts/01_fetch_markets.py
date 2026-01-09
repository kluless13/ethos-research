#!/usr/bin/env python3
"""
Step 1: Fetch all Ethos reputation markets.

Each market represents a person whose reputation is being traded.
This gives us the universe of subjects we can analyze.

Output: data/raw/markets.json
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ethos_client import EthosClient


def main():
    output_dir = Path(__file__).parent.parent / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "markets.json"
    
    print("=" * 60)
    print("ETHOS RESEARCH: Fetching All Markets")
    print("=" * 60)
    
    with EthosClient() as client:
        # Get stats first
        stats = client.get_profile_stats()
        print(f"\n📊 Ethos Network Stats:")
        print(f"   Active profiles: {stats['activeProfiles']:,}")
        print(f"   Invites available: {stats['invitesAvailable']:,}")
        
        # Fetch all markets
        print(f"\n🔄 Fetching all markets...")
        
        markets = []
        for i, market in enumerate(client.iter_all_markets(batch_size=100)):
            markets.append(market)
            
            if (i + 1) % 500 == 0:
                print(f"   Fetched {i + 1:,} markets...")
        
        print(f"\n✅ Fetched {len(markets):,} total markets")
        
        # Quick analysis
        with_twitter = sum(1 for m in markets if m.get("user", {}).get("username"))
        with_activity = sum(1 for m in markets if m["trustVotes"] > 1 or m["distrustVotes"] > 1)
        
        print(f"\n📈 Market Analysis:")
        print(f"   With Twitter linked: {with_twitter:,} ({100*with_twitter/len(markets):.1f}%)")
        print(f"   With trading activity: {with_activity:,} ({100*with_activity/len(markets):.1f}%)")
        
        # Save
        output_data = {
            "fetched_at": datetime.utcnow().isoformat(),
            "total_markets": len(markets),
            "ethos_stats": stats,
            "markets": markets
        }
        
        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n💾 Saved to: {output_file}")
        print(f"   File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
        
        # Show sample
        print(f"\n📋 Sample markets (first 5 with activity):")
        active_markets = [m for m in markets if m["trustVotes"] > 1 or m["distrustVotes"] > 1][:5]
        for m in active_markets:
            user = m.get("user", {})
            handle = user.get("username", "???")
            score = user.get("score", 0)
            print(f"   @{handle}: score={score}, trust={m['trustVotes']}, distrust={m['distrustVotes']}")


if __name__ == "__main__":
    main()

