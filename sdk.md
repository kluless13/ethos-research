# Ethos SDK Usage Guide

This document covers how to use the official Ethos SDKs for research and development.

## Installation

### Python SDK

```bash
pip install ethos-py
```

### TypeScript SDK

```bash
npm install ethos-ts-sdk
```

---

## Python SDK (`ethos-py`)

### Quick Start

```python
from ethos import Ethos

client = Ethos()

# Your code here...

client.close()
```

### Network Stats

```python
stats = client.profiles.stats()

print(stats.active_profiles)     # 35,833
print(stats.invites_available)   # 39,310
```

### Fetching Markets

Markets represent reputation markets where users can trade trust/distrust votes.

```python
# Iterate through all markets (lazy pagination)
for market in client.markets.list():
    print(market.profile_id)      # The Ethos profile ID
    print(market.trust_votes)     # Number of trust votes
    print(market.distrust_votes)  # Number of distrust votes
    print(market.trust_price)     # Trust price (0.0 to 1.0)
    print(market.total_volume)    # Total trading volume
```

**Market Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `profile_id` | int | Ethos profile ID |
| `trust_votes` | int | Number of trust votes |
| `distrust_votes` | int | Number of distrust votes |
| `trust_price` | float | Trust price (0.0-1.0) |
| `total_volume` | float | Total trading volume |

### Fetching Vouches

Vouches represent trust relationships where one user stakes ETH on another.

```python
# Iterate through all vouches
for vouch in client.vouches.list():
    print(vouch.author_profile_id)   # Who gave the vouch
    print(vouch.target_profile_id)   # Who received the vouch
    print(vouch.staked)              # Amount staked (wei)
    print(vouch.is_active)           # Whether vouch is active

# Get vouches for a specific profile
received = client.vouches.for_profile(6694)  # Vouches received
given = client.vouches.by_profile(6694)      # Vouches given

print(f"Received {len(received)} vouches")
print(f"Given {len(given)} vouches")
```

**Vouch Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `author_profile_id` | int | Profile ID of voucher |
| `target_profile_id` | int | Profile ID of vouchee |
| `staked` | str | Staked amount in wei |
| `is_active` | bool | Whether vouch is active |
| `amount_eth` | float | Staked amount in ETH |

### User Lookup

```python
# Look up by Twitter handle
user = client.users.get_by_twitter("edoweb3")

print(user.id)                           # 1945278
print(user.profile_id)                   # 6694
print(user.username)                     # edoweb3
print(user.score)                        # 1783 (credibility score)
print(user.xp_total)                     # 122887
print(user.stats.vouch.received.count)   # 24 vouches received
print(user.stats.vouch.given.count)      # 25 vouches given

# Other lookup methods
user = client.users.get_by_address("0x1234...")
user = client.users.get_by_profile_id(6694)
user = client.users.get_by_discord("690326861091438693")
user = client.users.get_by_telegram("788216335")
user = client.users.get_by_farcaster("1117623")
```

### Available Resources

| Resource | Description |
|----------|-------------|
| `client.profiles` | Profile stats and listing |
| `client.users` | User lookups (Twitter, address, etc.) |
| `client.markets` | Reputation markets |
| `client.vouches` | Vouch relationships |
| `client.reviews` | Reviews between users |
| `client.activities` | On-chain activity feed |
| `client.scores` | Credibility scores |
| `client.votes` | Market votes |
| `client.xp` | XP/experience data |

---

## TypeScript SDK (`ethos-ts-sdk`)

### Quick Start

```typescript
import { Ethos } from 'ethos-ts-sdk';

const client = new Ethos();

// Your code here...
```

### Fetching Markets

```typescript
// Async generator for efficient pagination
for await (const market of client.markets.list()) {
  console.log(market.profileId);      // 15172
  console.log(market.trustVotes);     // 492
  console.log(market.distrustVotes);  // 1
  console.log(market.trustPrice);     // 0.50 (50%)
  console.log(market.totalVolume);    // Total volume
}

// Get all markets as array
const allMarkets = await client.markets.listAll();

// Top markets by volume
const topByVolume = await client.markets.topByVolume(10);

// Most trusted markets
const mostTrusted = await client.markets.mostTrusted(10);
```

**Market Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `profileId` | number | Ethos profile ID |
| `trustVotes` | number | Number of trust votes |
| `distrustVotes` | number | Number of distrust votes |
| `trustPrice` | number | Trust price (0.0-1.0) |
| `totalVolume` | number | Total trading volume |
| `trustPercentage` | number | Trust as percentage (0-100) |
| `marketSentiment` | string | "bullish", "bearish", or "neutral" |

### Fetching Vouches

```typescript
// Async generator for pagination
for await (const vouch of client.vouches.list()) {
  console.log(vouch.authorProfileId);   // Who gave the vouch
  console.log(vouch.subjectProfileId);  // Who received it
  console.log(vouch.amountEth);         // Staked amount in ETH
  console.log(vouch.isActive);          // Whether active
}

// Get all vouches as array
const allVouches = await client.vouches.listAll();

// Vouches for a specific profile
const received = await client.vouches.forProfile(6694);
const given = await client.vouches.byProfile(6694);

// Check if vouch exists between two profiles
const vouch = await client.vouches.between(voucher_id, target_id);
```

**Vouch Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `authorProfileId` | number | Profile ID of voucher |
| `subjectProfileId` | number | Profile ID of vouchee |
| `amountWei` | bigint | Staked amount in wei |
| `amountEth` | number | Staked amount in ETH |
| `isActive` | boolean | Whether vouch is active |
| `voucherId` | number | Alias for authorProfileId |
| `targetId` | number | Alias for subjectProfileId |

### Profile Lookup

```typescript
// Look up by Twitter handle
const profile = await client.profiles.getByTwitter('edoweb3');

console.log(profile.id);                    // 1945278
console.log(profile.score);                 // 1783
console.log(profile.xpTotal);               // 122887
console.log(profile.twitterHandle);         // edoweb3
console.log(profile.credibilityScore);      // Alias for score
console.log(profile.scoreLevel);            // "Reputable"
console.log(profile.vouchesReceivedCount);  // 24
console.log(profile.vouchesGivenCount);     // 25

// Other lookup methods
const profile = await client.profiles.get(profileId);
const profile = await client.profiles.getByAddress("0x1234...");
const profile = await client.profiles.getByUserkey(userkey);

// Search profiles
const results = await client.profiles.search({ query: "vitalik" });
```

**Score Levels:**
| Score Range | Level |
|-------------|-------|
| 0-799 | Untrusted |
| 800-1199 | Questionable |
| 1200-1599 | Neutral |
| 1600-1999 | Reputable |
| 2000-2800 | Exemplary |

### Available Resources

| Resource | Description |
|----------|-------------|
| `client.profiles` | Profile lookups and search |
| `client.markets` | Reputation markets |
| `client.vouches` | Vouch relationships |
| `client.reviews` | Reviews between users |
| `client.activities` | On-chain activity feed |
| `client.scores` | Credibility scores |

---

## Research Examples

### Example 1: Find Top Vouchers

**Python:**
```python
from collections import defaultdict
from ethos import Ethos

client = Ethos()

voucher_counts = defaultdict(int)
for vouch in client.vouches.list():
    voucher_counts[vouch.author_profile_id] += 1

top_vouchers = sorted(voucher_counts.items(), key=lambda x: -x[1])[:10]
for profile_id, count in top_vouchers:
    print(f"Profile {profile_id}: {count} vouches given")

client.close()
```

**TypeScript:**
```typescript
import { Ethos } from 'ethos-ts-sdk';

const client = new Ethos();
const voucherCounts = new Map<number, number>();

for await (const vouch of client.vouches.list()) {
  const count = voucherCounts.get(vouch.authorProfileId) || 0;
  voucherCounts.set(vouch.authorProfileId, count + 1);
}

const topVouchers = [...voucherCounts.entries()]
  .sort((a, b) => b[1] - a[1])
  .slice(0, 10);

for (const [profileId, count] of topVouchers) {
  console.log(`Profile ${profileId}: ${count} vouches given`);
}
```

### Example 2: Analyze User's Network

**Python:**
```python
from ethos import Ethos

client = Ethos()

# Look up user
user = client.users.get_by_twitter("edoweb3")
print(f"@{user.username} (Score: {user.score})")

# Get their vouches
received = client.vouches.for_profile(user.profile_id)
given = client.vouches.by_profile(user.profile_id)

print(f"Vouches received: {len(received)}")
print(f"Vouches given: {len(given)}")

# Find mutual vouches
received_from = {v.author_profile_id for v in received}
given_to = {v.target_profile_id for v in given}
mutual = received_from & given_to

print(f"Mutual vouches: {len(mutual)}")

client.close()
```

### Example 3: Market Analysis

**TypeScript:**
```typescript
import { Ethos } from 'ethos-ts-sdk';

const client = new Ethos();

const markets: Market[] = [];
for await (const market of client.markets.list()) {
  markets.push(market);
  if (markets.length >= 100) break;
}

// Find most active markets
const active = markets
  .filter(m => m.trustVotes > 10 || m.distrustVotes > 10)
  .sort((a, b) => (b.trustVotes + b.distrustVotes) - (a.trustVotes + a.distrustVotes));

console.log(`Active markets: ${active.length}`);
for (const m of active.slice(0, 5)) {
  console.log(`Profile ${m.profileId}: ${m.trustVotes} trust, ${m.distrustVotes} distrust`);
}
```

---

## Test Results

Both SDKs have been tested and verified:

| SDK | Version | Tests | Status |
|-----|---------|-------|--------|
| **ethos-py** | 0.2.1 | 5/5 | ✅ Pass |
| **ethos-ts-sdk** | 0.1.0 | 4/4 | ✅ Pass |

### Run Tests

```bash
# Python SDK test
python scripts/sdk_test_python.py

# TypeScript SDK test
npx tsx scripts/sdk_test_typescript.ts
```

---

## Links

- **Python SDK**: [github.com/kluless13/ethos-python-sdk](https://github.com/kluless13/ethos-python-sdk) | [PyPI](https://pypi.org/project/ethos-py/)
- **TypeScript SDK**: [github.com/kluless13/ethos-ts-sdk](https://github.com/kluless13/ethos-ts-sdk) | [npm](https://www.npmjs.com/package/ethos-ts-sdk)
- **Ethos API Docs**: [developers.ethos.network](https://developers.ethos.network)
