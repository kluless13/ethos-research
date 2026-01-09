"""
TwitterAPI.io Client

Wrapper for twitterapi.io - 96% cheaper than official Twitter API.
Docs: https://docs.twitterapi.io
"""

import os
import httpx
import time
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class TwitterClient:
    """Client for TwitterAPI.io"""
    
    BASE_URL = "https://api.twitterapi.io"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TWITTERAPI_KEY")
        if not self.api_key:
            raise ValueError("TWITTERAPI_KEY not found. Set it in .env or pass directly.")
        
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        self._client = httpx.Client(headers=self.headers, timeout=30.0)
        self._request_count = 0
    
    def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make GET request."""
        url = f"{self.BASE_URL}{endpoint}"
        response = self._client.get(url, params=params)
        self._request_count += 1
        response.raise_for_status()
        return response.json()
    
    # ─────────────────────────────────────────────────────────────────
    # User Info
    # ─────────────────────────────────────────────────────────────────
    
    def get_user_info(self, username: str) -> dict:
        """
        Get user profile info.
        Cost: 18 credits (~$0.00018)
        """
        return self._get("/twitter/user/info", {"userName": username})
    
    # ─────────────────────────────────────────────────────────────────
    # Follow Checks
    # ─────────────────────────────────────────────────────────────────
    
    def check_follow_quick(self, source: str, target: str) -> Optional[bool]:
        """
        Quick follow check - only checks first page of followings (200 users).
        
        Returns:
            True if source follows target (found in first 200)
            False if not found in first 200 (may still follow if >200 followings)
            None if error/user not found
        
        Cost: ~15 credits
        """
        try:
            target_lower = target.lower()
            result = self._get("/twitter/user/followings", {"userName": source})
            followings = result.get("followings", [])
            
            for user in followings:
                username = user.get("userName", user.get("username", "")).lower()
                if username == target_lower:
                    return True
            
            return False
            
        except httpx.HTTPStatusError:
            return None
    
    
    # ─────────────────────────────────────────────────────────────────
    # Interaction Search
    # ─────────────────────────────────────────────────────────────────
    
    def search_interactions(self, from_user: str, to_user: str, limit: int = 20) -> dict:
        """
        Search for tweets from one user mentioning/replying to another.
        Cost: 15 credits per 20 tweets (~$0.00015)
        
        Uses Twitter search syntax: from:userA @userB OR from:userA to:userB
        """
        # Search for mentions and replies
        query = f"from:{from_user} (@{to_user} OR to:{to_user})"
        
        try:
            result = self._get("/twitter/tweet/advanced_search", {
                "query": query,
                "queryType": "Latest"
            })
            
            tweets = result.get("tweets", result.get("data", {}).get("tweets", []))
            
            return {
                "query": query,
                "count": len(tweets),
                "tweets": tweets[:limit]
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"query": query, "count": 0, "tweets": []}
            raise
    
    def has_interaction(self, from_user: str, to_user: str) -> bool:
        """
        Quick check if from_user has ever mentioned/replied to to_user.
        Returns True if any interaction found.
        """
        result = self.search_interactions(from_user, to_user, limit=1)
        return result["count"] > 0
    
    # ─────────────────────────────────────────────────────────────────
    # Batch Operations
    # ─────────────────────────────────────────────────────────────────
    
    def analyze_vouch_pair(self, voucher: str, vouchee: str) -> dict:
        """
        Analyze a vouch pair's Twitter relationship.
        
        Checks:
        1. Interactions (mentions/replies) - most reliable signal
        2. Follow relationship (quick check, first 200 followings only)
        
        Cost: ~60 credits (~$0.0006) per pair
        
        Returns dict with relationship data and authenticity score.
        """
        result = {
            "voucher": voucher,
            "vouchee": vouchee,
            "voucher_follows_vouchee": None,
            "vouchee_follows_voucher": None,
            "mutual_follow": None,
            "voucher_mentions_vouchee": False,
            "vouchee_mentions_voucher": False,
            "interaction_count": 0,
            "any_interaction": False,
            "authenticity_score": 0.0
        }
        
        # Check interactions (most reliable)
        try:
            v_to_e = self.search_interactions(voucher, vouchee, limit=5)
            result["voucher_mentions_vouchee"] = v_to_e["count"] > 0
            result["interaction_count"] += v_to_e["count"]
            time.sleep(0.15)
        except Exception:
            pass
        
        try:
            e_to_v = self.search_interactions(vouchee, voucher, limit=5)
            result["vouchee_mentions_voucher"] = e_to_v["count"] > 0
            result["interaction_count"] += e_to_v["count"]
            time.sleep(0.15)
        except Exception:
            pass
        
        result["any_interaction"] = result["voucher_mentions_vouchee"] or result["vouchee_mentions_voucher"]
        
        # Quick follow check (first 200 followings only)
        try:
            result["voucher_follows_vouchee"] = self.check_follow_quick(voucher, vouchee)
            time.sleep(0.15)
        except Exception:
            pass
        
        try:
            result["vouchee_follows_voucher"] = self.check_follow_quick(vouchee, voucher)
        except Exception:
            pass
        
        # Calculate mutual (only if both checks succeeded)
        if result["voucher_follows_vouchee"] is not None and result["vouchee_follows_voucher"] is not None:
            result["mutual_follow"] = result["voucher_follows_vouchee"] and result["vouchee_follows_voucher"]
        
        # Calculate authenticity score
        # Interaction is the strongest signal (0.5)
        # Follow is weaker signal (0.3)
        # Mutual follow bonus (0.2)
        score = 0.0
        if result["any_interaction"]:
            score += 0.5
        if result["voucher_follows_vouchee"]:
            score += 0.3
        if result["mutual_follow"]:
            score += 0.2
        
        result["authenticity_score"] = score
        
        return result
    
    @property
    def request_count(self) -> int:
        """Number of API requests made."""
        return self._request_count
    
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
    print("Testing TwitterAPI.io client...")
    
    with TwitterClient() as client:
        # Test: Get user info
        print("\n1. Testing get_user_info...")
        info = client.get_user_info("elonmusk")
        print(f"   @elonmusk: {info.get('data', {}).get('followers', 'N/A')} followers")
        
        print(f"\n✅ Test complete. Requests made: {client.request_count}")

