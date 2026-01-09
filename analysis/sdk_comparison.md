# SDK Comparison: ethos-py vs Our Current Approach

## TL;DR

The **ethos-py SDK** makes our research code **cleaner, type-safe, and more maintainable**. We should migrate.

---

## Side-by-Side Comparison

### Getting Vouches for a User

**Our Current Code** (`src/ethos_client.py`):
```python
def iter_vouches_for_subject(self, profile_id: int, batch_size: int = 100) -> Iterator[dict]:
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
```

**With ethos-py SDK**:
```python
client = Ethos()
vouches = client.vouches.for_profile(profile_id)  # Returns list[Vouch]
```

**Improvement**: 20 lines → 1 line. Pagination handled automatically.

---

### Getting User by Twitter Handle

**Our Current Code**:
```python
def get_user_by_twitter(self, twitter_handle: str) -> dict:
    return self._get(f"/user/by/x/{twitter_handle}")

# Returns untyped dict, have to dig into structure
user = client.get_user_by_twitter("serpinxbt")
handle = user.get("username")  # Hope the key exists
score = user.get("score", 0)   # Manual defaults
```

**With ethos-py SDK**:
```python
user = client.users.get_by_twitter("serpinxbt")
# Returns typed User object with IDE autocomplete
handle = user.username        # Type-checked
score = user.score           # Type-checked
twitter = user.twitter_handle # Convenience property
```

**Improvement**: Type safety, IDE autocomplete, cleaner properties.

---

### Getting Market Data

**Our Current Code**:
```python
def iter_all_markets(self, batch_size: int = 100) -> Iterator[dict]:
    offset = 0
    total = None
    
    while True:
        result = self.get_markets(limit=batch_size, offset=offset)
        # ... 15 more lines of pagination logic
```

**With ethos-py SDK**:
```python
# Iterate all markets
for market in client.markets.list():
    print(f"{market.trust_votes} / {market.distrust_votes}")

# Get top markets
top = client.markets.most_trusted(limit=10)
bottom = client.markets.most_distrusted(limit=10)
volume = client.markets.top_by_volume(limit=10)
```

**Improvement**: Built-in queries for common research patterns.

---

## What the SDK Provides

### 1. **Typed Models with Properties**

```python
class Vouch(BaseModel):
    author_profile_id: int
    target_profile_id: int
    balance: str  # wei as string
    
    @property
    def amount_eth(self) -> float:
        """Get the vouch amount in ETH."""
        return self.amount_wei / 1e18
    
    @property
    def is_active(self) -> bool:
        """Check if the vouch is currently active."""
        return self.staked and not self.archived
```

No more manual wei → ETH conversion or checking if vouch is active.

### 2. **Automatic Pagination**

All `.list()` methods return iterators that automatically paginate:

```python
# This fetches ALL vouches, handling pagination transparently
for vouch in client.vouches.list():
    process(vouch)
```

### 3. **Async Support**

```python
async with AsyncEthos() as client:
    vouches = await client.vouches.for_profile(12345)
    # Can run multiple requests concurrently
```

### 4. **Built-in Research Helpers**

From `examples/research_export.py`:
- `export_vouch_network()` — CSV export of vouches
- `export_profiles_with_twitter()` — Profiles with Twitter handles
- `analyze_score_distribution()` — Score breakdown

---

## Available Resources

| Resource | Key Methods |
|----------|-------------|
| `client.profiles` | `.get()`, `.get_by_twitter()`, `.list()`, `.search()`, `.recent()` |
| `client.vouches` | `.list()`, `.for_profile()`, `.by_profile()`, `.between()` |
| `client.reviews` | `.list()`, `.for_profile()`, `.positive_for()`, `.negative_for()` |
| `client.scores` | `.get()`, `.breakdown()` |
| `client.users` | `.get_by_twitter()`, `.bulk_by_twitter()`, `.search()` |
| `client.markets` | `.list()`, `.most_trusted()`, `.most_distrusted()`, `.top_by_volume()` |
| `client.activities` | `.list()`, `.recent()`, `.vouches()`, `.reviews()` |
| `client.votes` | `.list()`, `.upvotes_for()`, `.downvotes_for()` |
| `client.invitations` | `.list()`, `.by_sender()`, `.check_eligibility()` |

---

## Migration Plan

### Step 1: Install SDK
```bash
pip install ethos-py
```

### Step 2: Update Imports
```python
# Before
from ethos_client import EthosClient

# After  
from ethos import Ethos
```

### Step 3: Simplify Data Collection Scripts

**Before** (`02_fetch_vouches.py`):
```python
with EthosClient() as client:
    vouches = []
    for i, vouch in enumerate(client.iter_all_vouches(batch_size=100)):
        vouches.append(vouch)
        if (i + 1) % 1000 == 0:
            print(f"   Fetched {i + 1:,} vouches...")
```

**After**:
```python
with Ethos() as client:
    vouches = list(client.vouches.list())
    print(f"Fetched {len(vouches):,} vouches")
```

### Step 4: Use Typed Objects in Analysis

**Before**:
```python
# Digging into dicts
author_handle = vouch.get("authorUser", {}).get("username")
subject_handle = vouch.get("subjectUser", {}).get("username")
staked_wei = vouch.get("staked", 0)
```

**After**:
```python
# Clean object access
author_id = vouch.author_profile_id
target_id = vouch.target_profile_id
staked_eth = vouch.amount_eth
```

---

## What We Keep

The **TwitterAPI.io client** (`twitter_client.py`) stays — the SDK only covers Ethos, not Twitter.

Our **deep dive analysis logic** stays — the SDK handles data fetching, we handle the analysis/scoring.

---

## Recommendation

**Migrate to ethos-py for data collection, keep our analysis scripts.**

Benefits:
- Cleaner code (fewer lines)
- Type safety (catch bugs earlier)
- Automatic pagination (no manual offset handling)
- Maintained library (updates when API changes)

The SDK is at https://github.com/kluless13/ethos-python-sdk and `pip install ethos-py`.

