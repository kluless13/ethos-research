# Ethos Network Research

## On-Chain Reputation Meets Off-Chain Proof

**Independent research validating whether Ethos Network vouches reflect genuine social relationships.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

| SDK | Version | Downloads | Coverage |
|-----|---------|-----------|----------|
| **ethos-py** | [![PyPI](https://img.shields.io/pypi/v/ethos-py.svg)](https://pypi.org/project/ethos-py/) | [![Downloads](https://img.shields.io/pypi/dm/ethos-py.svg)](https://pypi.org/project/ethos-py/) | [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://pypi.org/project/ethos-py/) |
| **ethos-ts-sdk** | [![npm](https://img.shields.io/npm/v/ethos-ts-sdk.svg)](https://www.npmjs.com/package/ethos-ts-sdk) | [![Downloads](https://img.shields.io/npm/dm/ethos-ts-sdk.svg)](https://www.npmjs.com/package/ethos-ts-sdk) | [![Coverage](https://img.shields.io/badge/coverage-97.78%25-brightgreen.svg)](https://github.com/kluless13/ethos-ts-sdk) |

---

<p align="center">
  <img src="article%202.png" alt="Ethos Research Article" width="700">
</p>

---

## The Research Question

> **When someone stakes ETH to vouch for another person on Ethos, do they actually have a real social relationship?**

Ethos Network lets users stake cryptocurrency to vouch for others' reputations. But are these vouches meaningful signals of trust, or just speculative behavior?

**We tested this by cross-referencing on-chain vouches with Twitter engagement data.**

---

## Key Findings

<table>
<tr>
<td width="50%">

### @serpinxbt
**Most vouched user on Ethos**

| Metric | Value |
|--------|-------|
| Vouchers analyzed | 242 |
| **Twitter interaction** | **72%** |
| Bidirectional engagement | 50% |
| Inner circle | 45% |
| Suspicious accounts | 1.7% |

</td>
<td width="50%">

### @CrypSaf
**Second most vouched user**

| Metric | Value |
|--------|-------|
| Vouchers analyzed | 138 |
| **Twitter interaction** | **88%** |
| Bidirectional engagement | 83% |
| Inner circle | 78% |
| Suspicious accounts | 0.7% |

</td>
</tr>
</table>

### The Verdict
```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   72-88% of people who vouch on Ethos have actually interacted         │
│   with that person on Twitter.                                          │
│                                                                         │
│   Ethos vouches capture REAL social relationships.                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Vouch Authenticity Distribution

For @serpinxbt (242 vouchers):
```
Relationship Quality          Count    Percentage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Inner Circle  ████████████████████░░░░░░░░░░  110    45.5%   ← Frequent, two-way engagement
Active        █████░░░░░░░░░░░░░░░░░░░░░░░░░   30    12.4%   ← Regular interaction
Passive       ███████░░░░░░░░░░░░░░░░░░░░░░░   46    19.0%   ← One-way follows/mentions
Weak          ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░   16     6.6%   ← Minimal connection
None          █████░░░░░░░░░░░░░░░░░░░░░░░░░   36    14.9%   ← No Twitter relationship
Suspicious    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    4     1.7%   ← Potential bots/sybils
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                               242   100.0%
```

**77% of vouchers have a verifiable Twitter relationship** (inner circle + active + passive).

---

## What This Proves

### 1. Ethos Vouches Are Meaningful
When someone stakes ETH to vouch for you, they almost certainly have engaged with you on Twitter. This isn't speculation—it's social proof with financial commitment.

### 2. Staking Creates Natural Sybil Resistance
Only **1-2% of vouchers** show suspicious patterns (new accounts, low followers, bot-like behavior). The economic cost of vouching filters out bad actors.

### 3. High-Score Users Have Genuine Networks
Users with high Ethos scores (like @serpinxbt with 2,478) aren't gaming the system—they have extensive, verifiable social connections.

### 4. Interaction > Follows
**72% interact, but only 36% follow.** Twitter follows undercount relationships. Ethos vouches may capture social connections that follow graphs miss.

---

## ethos-py SDK

We built an **official Python SDK** for the Ethos API to power this research:
```bash
pip install ethos-py
```
```python
from ethos import Ethos

client = Ethos()

# Get a user's profile
user = client.users.get_by_twitter("serpinxbt")
print(f"{user.username}: Score {user.score}")

# Get all vouches for a profile
for vouch in client.vouches.for_profile(user.profile_id):
    print(f"Vouched by {vouch.author_profile_id}, staked {vouch.amount_eth} ETH")

# Analyze markets
for market in client.markets.most_trusted(limit=10):
    print(f"{market.trust_votes} trust / {market.distrust_votes} distrust")
```

**Features:**
- Automatic pagination
- Fully typed (Pydantic models)
- Async support
- Built-in research helpers

**PyPI:** [pypi.org/project/ethos-py](https://pypi.org/project/ethos-py/)
**GitHub:** [github.com/kluless13/ethos-python-sdk](https://github.com/kluless13/ethos-python-sdk)

---

## SDK vs Raw API: Why We Built ethos-py

This research started with raw API calls. It was painful. So we built an SDK.

### Getting Vouches for a User

**Raw API approach (what we started with):**
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

**With ethos-py SDK:**
```python
client = Ethos()
vouches = client.vouches.for_profile(profile_id)  # That's it.
```

**20 lines → 1 line.** Pagination handled automatically.

### Getting User by Twitter Handle

**Raw API approach:**
```python
user = client.get_user_by_twitter("serpinxbt")
handle = user.get("username")  # Hope the key exists
score = user.get("score", 0)   # Manual defaults
```

**With ethos-py SDK:**
```python
user = client.users.get_by_twitter("serpinxbt")
handle = user.username        # Type-checked, IDE autocomplete
score = user.score           # Type-checked
```

### Available SDK Resources

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

Full SDK vs API comparison: [`analysis/sdk_comparison.md`](analysis/sdk_comparison.md)

---

## Repository Structure
```
ethos-research/
├── README.md                 # You are here
├── requirements.txt          # Python dependencies
├── .env.example              # Configuration template (copy to .env)
├── ethosapi.md               # Ethos API documentation notes
│
├── src/                      # Source code
│   ├── ethos_client.py       # Ethos API client (raw, pre-SDK approach)
│   └── twitter_client.py     # Twitter API client (TwitterAPI.io)
│
├── scripts/                  # Data collection pipeline (run in order)
│   ├── 01_fetch_markets.py   # Step 1: Fetch all 219 reputation markets
│   ├── 02_fetch_vouches.py   # Step 2: Fetch all 53,400+ vouches
│   ├── 03_fetch_twitter.py   # Step 3: Get Twitter handles for vouchers
│   └── 04_deep_dive_market.py # Step 4: Deep analysis of a specific market
│
├── data/                     # Generated data (see "Data Files" below)
│   └── analysis/             # Final analysis outputs (committed)
│       ├── serpinxbt_deep_dive.json   # 242 vouchers analyzed
│       └── crypsaf_deep_dive.json     # 138 vouchers analyzed
│
└── analysis/                 # Research documentation
    ├── serpinxbt_case_study.md   # Full case study: @serpinxbt (72% verified)
    ├── crypsaf_case_study.md     # Full case study: @CrypSaf (88% verified)
    └── sdk_comparison.md         # Why we built ethos-py (SDK vs raw API)
```

---

## Data Files Explained

### What's Committed (in `data/analysis/`)

| File | Records | Size | Description |
|------|---------|------|-------------|
| `serpinxbt_deep_dive.json` | 242 | ~7MB | Per-voucher analysis for @serpinxbt |
| `crypsaf_deep_dive.json` | 138 | ~6MB | Per-voucher analysis for @CrypSaf |

Each record contains:
- **Voucher's Twitter profile**: followers, following, account age, verification status
- **Interaction counts**: voucher → subject mentions, subject → voucher mentions
- **Follow relationship**: mutual, one-way, or none
- **Relationship score**: 0.0 - 1.0 (calculated from above signals)
- **Credibility score**: 0.0 - 1.0 (is the voucher account legit?)
- **Tier classification**: inner_circle, active, passive, weak, none, or suspicious

### What's Generated by Scripts (gitignored)

These files are too large to commit. Run the pipeline to generate them:

| File | Records | Description |
|------|---------|-------------|
| `data/raw/markets.json` | 219 | All Ethos reputation markets |
| `data/raw/vouches.json` | 53,400+ | All on-chain vouch transactions |
| `data/processed/twitter_pairs.json` | 52,463 | Vouch pairs with Twitter handles |

### Data Collection Pipeline
```
Ethos API                          TwitterAPI.io
    │                                    │
    ▼                                    ▼
┌─────────┐    ┌─────────┐    ┌─────────────────┐    ┌──────────┐
│ Markets │───▶│ Vouches │───▶│ Twitter Pairs   │───▶│ Analysis │
│   219   │    │ 53,400  │    │ Follow + Engage │    │  Scores  │
└─────────┘    └─────────┘    └─────────────────┘    └──────────┘
     │              │                  │                   │
     ▼              ▼                  ▼                   ▼
  Script 01     Script 02          Script 03           Script 04
```

---

## Methodology

### Relationship Score (0.0 - 1.0)

For each vouch pair (A vouched for B):
```python
score = 0.0

# Interaction frequency (strongest signal)
if interactions >= 10:  score += 0.50
elif interactions >= 3: score += 0.35
elif interactions >= 1: score += 0.20

# Bidirectional bonus
if A_mentions_B and B_mentions_A:
    score += 0.20

# Follow relationships
if A_follows_B: score += 0.15
if B_follows_A: score += 0.15
```

### Relationship Tiers

| Tier | Criteria | Interpretation |
|------|----------|----------------|
| **Inner Circle** | Score ≥ 0.7 + bidirectional | Real friends, frequent engagement |
| **Active** | Score ≥ 0.5 | Regular interaction |
| **Passive** | Score ≥ 0.2 | Follows or occasional mentions |
| **Weak** | Score > 0 | Minimal connection |
| **None** | Score = 0 | No Twitter relationship found |
| **Suspicious** | Low score + red flags | New account, low followers, bot patterns |

### Credibility Score (0.0 - 1.0)

We also score each voucher's account credibility:
```python
score = 0.0

# Follower count
if followers >= 10000: score += 0.30
elif followers >= 1000: score += 0.20
elif followers >= 100:  score += 0.10

# Account age
if age_days >= 730: score += 0.20  # 2+ years
elif age_days >= 365: score += 0.15
elif age_days >= 180: score += 0.10

# Follower ratio (anti-bot signal)
if followers/following > 2: score += 0.10

# Verification
if blue_verified: score += 0.10

# Ethos score
if ethos_score >= 1500: score += 0.20
elif ethos_score >= 1000: score += 0.10
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Twitter API access via [TwitterAPI.io](https://twitterapi.io) (or Twitter API v2)
- (Optional) Ethos API key for higher rate limits

### Setup
```bash
# Clone the repo
git clone https://github.com/kluless13/ethos-research.git
cd ethos-research

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (see .env.example for all options)
```

### Run the Full Pipeline
```bash
# Step 1: Fetch all reputation markets from Ethos
python scripts/01_fetch_markets.py
# Output: data/raw/markets.json (219 markets)

# Step 2: Fetch all vouches
python scripts/02_fetch_vouches.py
# Output: data/raw/vouches.json (53,400+ vouches)

# Step 3: Get Twitter handles for vouch pairs
python scripts/03_fetch_twitter.py
# Output: data/processed/twitter_pairs.json

# Step 4: Deep dive on a specific market
python scripts/04_deep_dive_market.py serpinxbt --yes
# Output: data/analysis/serpinxbt_deep_dive.json
```

### Analyze Any Ethos User
```bash
python scripts/04_deep_dive_market.py <twitter_handle> --yes
```

This will:
1. Find the user's Ethos profile
2. Fetch all their vouchers
3. Cross-reference each voucher with Twitter data
4. Score and classify each relationship
5. Output detailed JSON analysis to `data/analysis/<handle>_deep_dive.json`

---

## Case Studies

Detailed analysis reports for the two most-vouched users:

| User | Vouchers | Verified Real | Suspicious | Report |
|------|----------|---------------|------------|--------|
| @serpinxbt | 242 | 72% | 1.7% | [`analysis/serpinxbt_case_study.md`](analysis/serpinxbt_case_study.md) |
| @CrypSaf | 138 | 88% | 0.7% | [`analysis/crypsaf_case_study.md`](analysis/crypsaf_case_study.md) |

---

## Upcoming Research

Some ideas I had:

- [ ] **Full market analysis** — All 200+ markets with vouchers
- [ ] **Temporal analysis** — Do interactions precede vouches, or follow them?
- [ ] **Stake correlation** — Do larger ETH stakes correlate with stronger relationships?
- [ ] **Network clustering** — Do vouchers know each other? Sybil ring detection
- [ ] **Score prediction** — Can Twitter engagement predict Ethos score?

**Want to contribute?** Open an issue or submit a PR.

---

## References

- [Ethos Network](https://ethos.network) — On-chain reputation protocol
- [Ethos API Documentation](https://docs.ethos.network) — API reference
- [ethos-py SDK](https://github.com/kluless13/ethos-py) — Python SDK for Ethos API
- [ethos-ts-dsk](https://github.com/kluless13/ethos-ts-sdk) - Typescript SDK for Ethos API
- [TwitterAPI.io](https://twitterapi.io) — Twitter data provider

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  <i>Do people trust who they say they trust?</i><br>
  <b>The data says yes.</b>
</p>