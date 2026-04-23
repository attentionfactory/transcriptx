# Referral Loops

## What's live

- **+10 credits per successful referral** (signup + first transcript).
- **Welcome bar** for referred visitors.
- **MX-record check** on signup to block disposable emails (referral abuse mitigation).

## Ideas to test

### 1. Share-the-transcript loop
When a user finishes a transcript, surface a "Share this transcript" button. If someone clicks a shared transcript link and signs up, credit the original user.
- **Hypothesis:** transcripts get shared anyway (Slack, email, docs) — adding a lightweight attribution link is free virality.
- **Worked:** if ≥5% of finished transcripts get shared externally and ≥10% of clickthroughs signup.
- **Failed:** <2% share rate after 60 days → kill.
- **Cost:** ~1 day of eng.

### 2. Referral rewards for the referrer's referrer (2-tier)
Small bonus (+2 credits) when your referral refers someone.
- **Hypothesis:** encourages power-referrers.
- **Worked:** lifts per-user referral count ≥15%.
- **Failed:** no measurable lift after 90 days, or invites abuse spike.
- **Cost:** ~half day.

### 3. "Gift a transcript" flow
Logged-in user can send a free transcript credit to a friend via link. Recipient signs up to redeem.
- **Hypothesis:** gifting is a softer ask than "refer me a friend".
- **Worked:** 10%+ of active users send at least one gift.
- **Failed:** <2% usage → kill.

### 4. Embed badge for podcasters/creators
If a creator uses us for show notes, give them a "Transcribed by TranscriptX" badge with a referral link.
- **Hypothesis:** podcaster audiences are our ICP.
- **Worked:** 5+ creators use it and drive ≥20 signups/mo.
- **Failed:** creators see it as visual clutter and don't adopt.

### 5. Team-account referral kickback
When a referred user upgrades to a paid plan, referrer gets a full free month (on top of +10 credits).
- **Hypothesis:** paid conversion is the number that matters, not signup.
- **Worked:** paid-referral count ≥2× baseline.
- **Failed:** no shift → kill, it was just extra cost.

## Abuse guardrails to keep in mind

- Disposable email check (live).
- Rate-limit referrals per IP.
- Require referred user to complete at least one real transcript before credits unlock.
- Soft-cap credits per referrer per month (e.g., 50) to stop fraud rings.

## Kill criteria for the referral program overall

- If after 6 months <10% of signups come from referrals, the program isn't worth the maintenance burden — simplify to a bare-bones invite link with no rewards.
