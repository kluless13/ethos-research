# Case Study: @serpinxbt

**Do On-Chain Vouches Reflect Real Social Relationships?**

---

## Executive Summary

We analyzed all 242 vouchers for @serpinxbt, the most-vouched user on Ethos Network. **72% of vouchers have interacted with him on Twitter**, and **50% have bidirectional conversations**. Only 1.7% of vouchers show suspicious patterns. This strongly suggests Ethos vouches capture genuine social trust, not speculation or farming.

---

## Research Questions

| Question | Finding | Confidence |
|----------|---------|------------|
| **Q1:** Do vouchers interact with vouchees on Twitter? | **Yes** — 72% have interacted | HIGH |
| **Q2:** Does vouch graph overlap with follow graph? | **Partially** — 36% follow, but 72% interact | HIGH |
| **Q3:** Do high-score users have genuine connections? | **Yes** — serpinxbt (score: 2478) has 45% inner circle | HIGH |

---

## Subject Profile

| Attribute | Value |
|-----------|-------|
| Twitter | [@serpinxbt](https://twitter.com/serpinxbt) |
| Followers | 23,582 |
| Account Age | 3 years (Jan 2022) |
| Ethos Score | 2,478 (top tier) |
| Trust Votes | 1,398 |
| Distrust Votes | 204 |
| **Trust Ratio** | **87.3%** |
| Total Vouchers | 242 unique accounts |

---

## Methodology

### Data Sources
- **Ethos API**: Vouch transactions, user profiles, Ethos scores
- **TwitterAPI.io**: Follow relationships, tweet searches for interactions

### Analysis Per Voucher
For each of the 242 accounts that vouched for @serpinxbt:

1. **Profile Analysis**: Followers, account age, verification status
2. **Interaction Search**: Tweets from voucher mentioning/replying to serpinxbt
3. **Reverse Search**: Tweets from serpinxbt mentioning/replying to voucher
4. **Follow Check**: Does voucher follow serpinxbt? Does serpinxbt follow back?

### Scoring Model

**Relationship Score** (0.0 - 1.0):
```
+0.50  if 10+ interactions
+0.35  if 3-9 interactions
+0.20  if 1-2 interactions
+0.20  if bidirectional (both mention each other)
+0.15  if voucher follows subject
+0.15  if subject follows voucher back
```

**Relationship Tiers**:
| Tier | Criteria |
|------|----------|
| Inner Circle | Score ≥ 0.7 + bidirectional engagement |
| Active | Score ≥ 0.5 |
| Passive | Score ≥ 0.2 |
| Weak | Score > 0 |
| None | Score = 0 |
| Suspicious | Low score + red flags (new account, low followers) |

---

## Results

### Voucher Distribution by Relationship Tier

```
Inner Circle   ████████████████████░░░░░░░░░░   110 (45.5%)
Active         █████░░░░░░░░░░░░░░░░░░░░░░░░░    30 (12.4%)
Passive        ███████░░░░░░░░░░░░░░░░░░░░░░░    46 (19.0%)
Weak           ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░    16 ( 6.6%)
None           █████░░░░░░░░░░░░░░░░░░░░░░░░░    36 (14.9%)
Suspicious     ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░     4 ( 1.7%)
                                               ─────────────
                                                 242 (100%)
```

### Key Metrics

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Any Twitter Interaction** | 174 / 242 (71.9%) | Most vouchers have engaged with serpinxbt |
| **Bidirectional Interaction** | 121 / 242 (50.0%) | Half have two-way conversations |
| **Voucher Follows Subject** | ~36% | Lower than interaction rate |
| **Subject Follows Back** | 7 / 242 (2.9%) | Serpinxbt doesn't follow most vouchers |
| **Avg Relationship Score** | 0.46 | Moderate-to-strong relationships |
| **Avg Credibility Score** | 0.65 | Vouchers are generally credible accounts |

---

## Key Findings

### Finding 1: Vouches Reflect Real Engagement

**72% of vouchers have interacted with @serpinxbt on Twitter.**

This is the strongest evidence that Ethos vouches capture genuine relationships. When someone stakes ETH to vouch for serpinxbt, they're almost always someone who has actually engaged with him publicly.

### Finding 2: Interaction > Following

**36% of vouchers follow serpinxbt, but 72% have interacted.**

This reveals an important pattern: Twitter "follows" are a weaker signal than actual engagement. Many vouchers engage via replies and mentions without formally following. Our research validates using interaction data over follow data.

### Finding 3: Half Have Two-Way Relationships

**50% of vouchers have bidirectional interactions** (both parties have mentioned/replied to each other).

This indicates that vouches aren't just one-sided fandom — half represent mutual recognition. These are real relationships, not parasocial connections.

### Finding 4: Minimal Sybil Activity

**Only 4 accounts (1.7%) flagged as suspicious.**

Suspicious patterns detected:
- `@azrimkbr`: Abnormal follower/following ratio
- `@mybmwclub`: Low followers despite high Ethos score
- `@BoratXBT`: Very low follower count
- `@secr3t_aardvark`: Very low follower count

The extremely low suspicious rate suggests Ethos's vouching mechanism naturally filters out bad actors (staking ETH creates friction).

### Finding 5: Serpinxbt is a Hub, Not a Reciprocator

**Serpinxbt follows back only 2.9% of vouchers.**

This reveals his network position: he's a central figure that many people engage with, but he doesn't reciprocate follows. His high Ethos score reflects incoming trust, not mutual friend networks.

---

## Inner Circle Analysis

The **top 10 most-engaged vouchers** (by interaction count):

| Voucher | Interactions | Notable |
|---------|--------------|---------|
| @frankdegods | 40+ | NFT ecosystem figure |
| @1ncrypto | 40+ | Crypto Twitter active |
| @0xCragHack | 40+ | Also top-vouched on Ethos |
| @SendMyBags | 40+ | Regular engagement |
| @Jampzey | 40+ | Long-term interaction history |
| @0xQuit | 40+ | Crypto developer |
| @WazzCrypto | 40+ | Trading community |
| @PedroFounder | 40+ | Web3 builder |
| @crazino87 | 40+ | Consistent engagement |
| @PremiumSaltine_ | 40+ | Active CT participant |

These accounts represent serpinxbt's genuine network — people he regularly interacts with who have also vouched for him on Ethos.

---

## Conclusions

### Primary Research Question

> **When someone vouches for another person on Ethos, do they have a real social relationship?**

**Answer: Yes, in most cases.**

For @serpinxbt:
- **72%** of vouchers have Twitter interaction history
- **50%** have bidirectional engagement
- **45%** qualify as "inner circle" relationships
- Only **1.7%** show suspicious patterns

### Implications

1. **Ethos vouches are meaningful** — They correlate strongly with real-world (Twitter) social connections, not just speculation.

2. **Staking creates friction** — The 1.7% suspicious rate suggests that requiring ETH stakes filters out low-quality vouches.

3. **High-score users have genuine networks** — Serpinxbt's 2,478 Ethos score reflects real social capital built through actual engagement.

4. **Interaction > Follows** — Twitter follow relationships undercount actual engagement. Vouches may capture relationships that follow graphs miss.

---

## Limitations

1. **Single subject** — This analyzes only serpinxbt. Results may differ for other markets.

2. **Twitter search limitations** — API returns recent/popular tweets; older interactions may be missed.

3. **No temporal analysis** — We don't know if interactions happened before or after vouching.

4. **No stake amounts** — We didn't correlate relationship strength with ETH staked.

---

## Next Steps

1. **Replicate for top 5 markets** — Compare serpinxbt's pattern to other highly-vouched users
2. **Analyze low-score users** — Do users with low Ethos scores have weaker social ties?
3. **Temporal analysis** — Did vouchers interact before or after vouching?
4. **Stake correlation** — Do larger stakes correlate with stronger relationships?

---

## Data Files

| File | Description |
|------|-------------|
| `data/raw/vouches.json` | All 53,400 Ethos vouches |
| `data/raw/markets.json` | 219 reputation markets |
| `data/analysis/serpinxbt_deep_dive.json` | Full analysis output (242 vouchers) |

---

## Appendix: Scoring Formulas

### Relationship Score

```python
score = 0.0

# Interaction frequency (max 0.50)
interactions = voucher_to_subject + subject_to_voucher
if interactions >= 10: score += 0.50
elif interactions >= 3: score += 0.35
elif interactions >= 1: score += 0.20

# Bidirectionality bonus
if voucher_mentions_subject and subject_mentions_voucher:
    score += 0.20

# Follow relationships
if voucher_follows_subject: score += 0.15
if subject_follows_voucher: score += 0.15

# Cap at 1.0
relationship_score = min(score, 1.0)
```

### Credibility Score

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

# Follower ratio (anti-bot)
if followers/following > 2: score += 0.10

# Verification
if blue_verified: score += 0.10

# Ethos score
if ethos_score >= 1500: score += 0.20
elif ethos_score >= 1000: score += 0.10

credibility_score = min(score, 1.0)
```

---

*Analysis performed: January 2026*
*Data sources: Ethos Network API, TwitterAPI.io*

