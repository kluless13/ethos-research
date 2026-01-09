# 🔷 Ethos Network Research

## On-Chain Trust, Real-World Proof

**Independent research validating whether Ethos Network vouches reflect genuine social relationships.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![ethos-py](https://img.shields.io/pypi/v/ethos-py?label=ethos-py&color=green)](https://pypi.org/project/ethos-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🔬 The Research Question

> **When someone stakes ETH to vouch for another person on Ethos, do they actually have a real social relationship?**

Ethos Network lets users stake cryptocurrency to vouch for others' reputations. But are these vouches meaningful signals of trust, or just speculative behavior?

**We tested this by cross-referencing on-chain vouches with Twitter engagement data.**

---

## 📊 Key Findings

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

## 📈 Vouch Authenticity Distribution

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

## 🎯 What This Proves

### 1. Ethos Vouches Are Meaningful
When someone stakes ETH to vouch for you, they almost certainly have engaged with you on Twitter. This isn't speculation—it's social proof with financial commitment.

### 2. Staking Creates Natural Sybil Resistance
Only **1-2% of vouchers** show suspicious patterns (new accounts, low followers, bot-like behavior). The economic cost of vouching filters out bad actors.

### 3. High-Score Users Have Genuine Networks
Users with high Ethos scores (like @serpinxbt with 2,478) aren't gaming the system—they have extensive, verifiable social connections.

### 4. Interaction > Follows
**72% interact, but only 36% follow.** Twitter follows undercount relationships. Ethos vouches may capture social connections that follow graphs miss.

---

## 🛠️ ethos-py SDK

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
- 🔄 Automatic pagination
- 📝 Fully typed (Pydantic models)
- ⚡ Async support
- 🔍 Built-in research helpers

📦 **PyPI:** [pypi.org/project/ethos-py](https://pypi.org/project/ethos-py/)  
📂 **GitHub:** [github.com/kluless13/ethos-python-sdk](https://github.com/kluless13/ethos-python-sdk)

---

## 📁 Dataset

| File | Records | Description |
|------|---------|-------------|
| `markets.json` | 219 | Reputation markets (people being traded) |
| `vouches.json` | 53,400 | On-chain vouch transactions |
| `twitter_pairs` | 52,463 | Vouch pairs with Twitter handles |
| `*_deep_dive.json` | 380 | Detailed per-voucher analysis |

### Data Collection Pipeline

```
Ethos API                          TwitterAPI.io
    │                                    │
    ▼                                    ▼
┌─────────┐    ┌─────────┐    ┌─────────────────┐    ┌──────────┐
│ Markets │───▶│ Vouches │───▶│ Twitter Pairs   │───▶│ Analysis │
│   219   │    │ 53,400  │    │ Follow + Engage │    │  Scores  │
└─────────┘    └─────────┘    └─────────────────┘    └──────────┘
```

---

## 🧮 Methodology

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
| **Suspicious** | Low score + red flags | New account, low followers |

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/kluless13/ethos-research.git
cd ethos-research

# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run deep dive on any market
python scripts/04_deep_dive_market.py serpinxbt --yes
```

### Run Your Own Analysis

```bash
# Analyze any Ethos user
python scripts/04_deep_dive_market.py <twitter_handle> --yes

# Output: data/analysis/<handle>_deep_dive.json
```

---

## 🔮 Upcoming Research

This is **Phase 1** of our Ethos Network research. Coming soon:

- [ ] **Full market analysis** — All 200+ markets with vouchers
- [ ] **Temporal analysis** — Do interactions precede vouches, or follow them?
- [ ] **Stake correlation** — Do larger ETH stakes correlate with stronger relationships?
- [ ] **Network clustering** — Do vouchers know each other? Sybil ring detection
- [ ] **Score prediction** — Can Twitter engagement predict Ethos score?

**Want to contribute?** Open an issue or submit a PR.

---

## 📄 Case Studies

Detailed analysis reports:

- [`analysis/serpinxbt_case_study.md`](analysis/serpinxbt_case_study.md) — 242 vouchers, 72% authentic
- [`analysis/crypsaf_case_study.md`](analysis/crypsaf_case_study.md) — 138 vouchers, 88% authentic

---

## 📚 References

- [Ethos Network](https://ethos.network) — On-chain reputation protocol
- [Ethos API Documentation](https://docs.ethos.network) — API reference
- [ethos-py SDK](https://github.com/kluless13/ethos-python-sdk) — Python SDK for Ethos API
- [TwitterAPI.io](https://twitterapi.io) — Twitter data provider

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  <i>Do people trust who they say they trust?</i><br>
  <b>The data says yes.</b>
</p>
