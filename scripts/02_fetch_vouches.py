#!/usr/bin/env python3
"""
Step 2: Fetch all vouches from Ethos.

A vouch is when user A stakes ETH to vouch for user B.
This creates the social trust graph we want to analyze.

Output: data/raw/vouches.json
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ethos_client import EthosClient


def main():
    output_dir = Path(__file__).parent.parent / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "vouches.json"
    
    print("=" * 60)
    print("ETHOS RESEARCH: Fetching All Vouches")
    print("=" * 60)
    
    with EthosClient() as client:
        print(f"\n🔄 Fetching all vouches...")
        
        vouches = []
        for i, vouch in enumerate(client.iter_all_vouches(batch_size=100)):
            vouches.append(vouch)
            
            if (i + 1) % 1000 == 0:
                print(f"   Fetched {i + 1:,} vouches...")
        
        print(f"\n✅ Fetched {len(vouches):,} total vouches")
        
        # Analysis
        # Extract unique vouch pairs (author -> subject)
        vouch_pairs = set()
        twitter_pairs = []
        
        for v in vouches:
            author = v.get("authorUser", {})
            subject = v.get("subjectUser", {})
            
            author_id = v.get("authorProfileId")
            subject_id = v.get("subjectProfileId")
            
            if author_id and subject_id:
                vouch_pairs.add((author_id, subject_id))
            
            # Extract Twitter handles
            author_handle = author.get("username") if author else None
            subject_handle = subject.get("username") if subject else None
            
            if author_handle and subject_handle:
                twitter_pairs.append({
                    "author_twitter": author_handle,
                    "subject_twitter": subject_handle,
                    "author_profile_id": author_id,
                    "subject_profile_id": subject_id,
                    "author_score": author.get("score", 0) if author else 0,
                    "subject_score": subject.get("score", 0) if subject else 0,
                })
        
        print(f"\n📈 Vouch Analysis:")
        print(f"   Unique vouch relationships: {len(vouch_pairs):,}")
        print(f"   Pairs with both Twitter handles: {len(twitter_pairs):,}")
        
        # Who vouches the most?
        voucher_counts = defaultdict(int)
        for v in vouches:
            author = v.get("authorUser", {})
            if author and author.get("username"):
                voucher_counts[author["username"]] += 1
        
        top_vouchers = sorted(voucher_counts.items(), key=lambda x: -x[1])[:10]
        print(f"\n🏆 Top 10 Vouchers:")
        for handle, count in top_vouchers:
            print(f"   @{handle}: {count} vouches given")
        
        # Who receives the most vouches?
        vouchee_counts = defaultdict(int)
        for v in vouches:
            subject = v.get("subjectUser", {})
            if subject and subject.get("username"):
                vouchee_counts[subject["username"]] += 1
        
        top_vouchees = sorted(vouchee_counts.items(), key=lambda x: -x[1])[:10]
        print(f"\n⭐ Top 10 Most Vouched:")
        for handle, count in top_vouchees:
            print(f"   @{handle}: {count} vouches received")
        
        # Save
        output_data = {
            "fetched_at": datetime.utcnow().isoformat(),
            "total_vouches": len(vouches),
            "unique_pairs": len(vouch_pairs),
            "pairs_with_twitter": len(twitter_pairs),
            "vouches": vouches,
            "twitter_pairs": twitter_pairs,  # Pre-extracted for convenience
        }
        
        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n💾 Saved to: {output_file}")
        print(f"   File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()

