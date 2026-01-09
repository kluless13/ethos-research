"""
Ethos Network API Client

Simple wrapper for fetching data from Ethos Network API v2.
No authentication required - just identifies the client.
"""

import httpx
import json
import time
from pathlib import Path
from typing import Optional, Iterator
from datetime import datetime


class EthosClient:
    """Client for Ethos Network API v2."""
    
    BASE_URL = "https://api.ethos.network/api/v2"
    
    def __init__(self, client_name: str = "ethos-research"):
        self.client_name = client_name
        self.headers = {
            "X-Ethos-Client": client_name,
            "Content-Type": "application/json"
        }
        self._client = httpx.Client(headers=self.headers, timeout=30.0)
    
    def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make GET request to API."""
        url = f"{self.BASE_URL}{endpoint}"
        response = self._client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def _post(self, endpoint: str, data: dict) -> dict:
        """Make POST request to API."""
        url = f"{self.BASE_URL}{endpoint}"
        response = self._client.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    # ─────────────────────────────────────────────────────────────────
    # Markets
    # ─────────────────────────────────────────────────────────────────
    
    def get_markets(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "createdAt",
        order_direction: str = "desc"
    ) -> dict:
        """
        Get paginated list of reputation markets.
        
        Args:
            limit: Max 100 per request
            order_by: createdAt, marketCapWei, volumeTotalWei, etc.
            order_direction: asc or desc
        """
        return self._get("/markets", {
            "limit": limit,
            "offset": offset,
            "orderBy": order_by,
            "orderDirection": order_direction
        })
    
    def iter_all_markets(self, batch_size: int = 100) -> Iterator[dict]:
        """
        Iterate through ALL markets with automatic pagination.
        
        Yields individual market objects.
        """
        offset = 0
        total = None
        
        while True:
            result = self.get_markets(limit=batch_size, offset=offset)
            
            if total is None:
                total = result["total"]
                print(f"📊 Total markets to fetch: {total}")
            
            for market in result["values"]:
                yield market
            
            offset += batch_size
            if offset >= total:
                break
            
            # Be nice to the API
            time.sleep(0.2)
    
    def get_market_holders(
        self,
        profile_id: int,
        vote_type: Optional[str] = None,  # "trust" or "distrust"
        limit: int = 100,
        offset: int = 0
    ) -> dict:
        """Get users holding trust/distrust votes in a market."""
        params = {"limit": limit, "offset": offset}
        if vote_type:
            params["voteType"] = vote_type
        return self._get(f"/markets/{profile_id}/holders", params)
    
    # ─────────────────────────────────────────────────────────────────
    # Vouches
    # ─────────────────────────────────────────────────────────────────
    
    def get_vouches(
        self,
        subject_profile_ids: Optional[list[int]] = None,
        author_profile_ids: Optional[list[int]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> dict:
        """
        Query vouches with optional filters.
        
        Args:
            subject_profile_ids: Filter by who received the vouch
            author_profile_ids: Filter by who gave the vouch
        """
        data = {"limit": limit, "offset": offset}
        if subject_profile_ids:
            data["subjectProfileIds"] = subject_profile_ids
        if author_profile_ids:
            data["authorProfileIds"] = author_profile_ids
        return self._post("/vouches", data)
    
    def iter_vouches_for_subject(self, profile_id: int, batch_size: int = 100) -> Iterator[dict]:
        """Iterate through all vouches received by a profile."""
        offset = 0
        total = None
        
        while True:
            result = self.get_vouches(
                subject_profile_ids=[profile_id],
                limit=batch_size,
                offset=offset
            )
            
            if total is None:
                total = result["total"]
            
            for vouch in result["values"]:
                yield vouch
            
            offset += batch_size
            if offset >= total:
                break
            
            time.sleep(0.1)
    
    def iter_all_vouches(self, batch_size: int = 100) -> Iterator[dict]:
        """Iterate through ALL vouches (no filter)."""
        offset = 0
        total = None
        
        while True:
            result = self.get_vouches(limit=batch_size, offset=offset)
            
            if total is None:
                total = result["total"]
                print(f"🤝 Total vouches to fetch: {total}")
            
            for vouch in result["values"]:
                yield vouch
            
            offset += batch_size
            if offset >= total:
                break
            
            time.sleep(0.2)
    
    # ─────────────────────────────────────────────────────────────────
    # Users / Profiles
    # ─────────────────────────────────────────────────────────────────
    
    def get_user_by_twitter(self, twitter_handle: str) -> dict:
        """Look up Ethos user by Twitter/X handle."""
        return self._get(f"/user/by/x/{twitter_handle}")
    
    def get_users_by_twitter_batch(self, handles: list[str]) -> list[dict]:
        """Batch lookup users by Twitter handles (up to 500)."""
        return self._post("/users/by/x", {"accountIdsOrUsernames": handles})
    
    def get_user_by_profile_id(self, profile_id: int) -> dict:
        """Get user by Ethos profile ID."""
        return self._get(f"/user/by/profile-id/{profile_id}")
    
    def get_profiles(
        self,
        ids: Optional[list[int]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> dict:
        """Get paginated profiles list."""
        data = {"limit": limit, "offset": offset}
        if ids:
            data["ids"] = ids
        return self._post("/profiles", data)
    
    def get_profile_stats(self) -> dict:
        """Get overall profile statistics."""
        return self._get("/profiles/stats")
    
    # ─────────────────────────────────────────────────────────────────
    # Reviews
    # ─────────────────────────────────────────────────────────────────
    
    def get_review_count_between(self, author_key: str, subject_key: str) -> int:
        """Count reviews from author to subject."""
        return self._get("/reviews/count/between", {
            "authorUserKey": author_key,
            "subjectUserKey": subject_key
        })
    
    # ─────────────────────────────────────────────────────────────────
    # Utilities
    # ─────────────────────────────────────────────────────────────────
    
    @staticmethod
    def extract_twitter_handle(user: dict) -> Optional[str]:
        """Extract Twitter handle from user object."""
        # First check username field (usually the Twitter handle)
        if user.get("username"):
            return user["username"]
        
        # Fallback: parse from userkeys
        for key in user.get("userkeys", []):
            if key.startswith("service:x.com:username:"):
                return key.split(":")[-1]
        
        return None
    
    @staticmethod
    def extract_twitter_id(user: dict) -> Optional[str]:
        """Extract Twitter user ID from userkeys."""
        for key in user.get("userkeys", []):
            if key.startswith("service:x.com:") and not "username" in key:
                return key.split(":")[-1]
        return None
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


# ─────────────────────────────────────────────────────────────────────
# Quick test
# ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    with EthosClient() as client:
        # Test: Get stats
        stats = client.get_profile_stats()
        print(f"Active profiles: {stats['activeProfiles']}")
        
        # Test: Get first few markets
        markets = client.get_markets(limit=3)
        print(f"\nFirst 3 markets:")
        for m in markets["values"]:
            user = m.get("user")
            if user:
                handle = client.extract_twitter_handle(user)
                print(f"  - @{handle} (score: {user['score']}, trust: {m['trustVotes']}, distrust: {m['distrustVotes']})")

