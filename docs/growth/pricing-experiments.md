# Pricing Experiments

## What's live

- **Free:** 3 transcripts/month.
- **Pro:** $3.99/mo, unlimited.
- **Annual Pro:** discounted annual tier (see index.html for exact).
- Pricing displayed as `.99` format for price-anchor reasons.

## Hypotheses worth testing

### 1. Lifetime deal for early adopters
One-time payment, e.g., $49 for lifetime unlimited. Capped at N users.
- **Hypothesis:** converts price-sensitive researchers/students who hate subscriptions.
- **Worked:** sells out within 30 days without cannibalizing monthly.
- **Failed:** cannibalizes monthly signups or <20% of cap sells.

### 2. Usage-based tier
$0.10 per transcript, no monthly commitment.
- **Hypothesis:** captures the "I only need this twice a year" user.
- **Worked:** adds 10%+ net revenue without cannibalizing Pro.
- **Failed:** no lift → kill, complexity isn't worth it.

### 3. Student pricing
50% off with .edu email.
- **Hypothesis:** students are a big share of traffic (lecture transcription).
- **Worked:** .edu signups ≥15% of paid base and retention ≥ Pro baseline.
- **Failed:** low conversion or high churn.

### 4. Pro+ tier at $9.99
Adds: priority queue, batch upload, speaker diarization, API access.
- **Hypothesis:** power users (journalists, researchers, small content teams) will pay more for less waiting and batch.
- **Worked:** ≥5% of Pro users upgrade within 90 days.
- **Failed:** <2% upgrade → features are nice-to-haves, not willingness-to-pay drivers.

### 5. Free-tier calibration
A/B: 3/month vs 5/month vs 1/week.
- **Hypothesis:** current 3/month is either leaving activation on the table or giving away too much.
- **Worked:** one variant lifts paid conversion ≥10% without increasing costs disproportionately.
- **Failed:** all variants within noise.

## Things we are NOT testing

- **Raising the Pro price above $3.99.** The unlimited-for-$4 positioning is the wedge. Killing it kills the category.
- **Removing the free tier entirely.** The funnel starts there.
- **Adding a "Team" tier prematurely.** We don't have the multi-seat plumbing and the ICP isn't asking for it yet.

## Measurement

- Track signup → first transcript → paid conversion as three separate funnel steps.
- Track churn separately by acquisition source.
- Report monthly.
