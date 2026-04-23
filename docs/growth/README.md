# Growth

Working notebook for growth experiments, SEO bets, content plans, and referral/retention mechanics. **Not user-facing** — this folder is never served by Flask. It's the place to think out loud before committing to real pages, features, or campaigns.

## Operating principles

1. **Solve a specific Googled problem.** If nobody is typing the exact thing into a search bar, don't build a page for it. "Platform Index" is dead. "How to transcribe a Google Drive video" is alive.
2. **Lead with the 60-second answer.** Every guide, every landing page, every email. If someone bounces after the first paragraph, they should still have the answer.
3. **Honesty compounds.** Admit what we can't do (Instagram Stories are hard, Spaces recordings are flaky). Saves refunds, builds trust, and ranks because competitors won't say it.
4. **Free tier is the growth engine.** 3 free transcripts/month → plant a seed, let usage show value. Don't hide it.
5. **Referrals over ads.** +10 credits per referral is already live. Keep stacking referral + share-the-transcript loops before spending on paid.
6. **Ship, measure, kill.** Any experiment without a kill criterion is a roach motel for energy. Each doc below ends with "how we'd know it failed".

## Docs in this folder

- [`content-guides-backlog.md`](content-guides-backlog.md) — the list of how-to guides we should write, ranked by intent. Replaces the SEO-fluff guides currently in `GUIDES_CONTENT`.
- [`seo-strategy.md`](seo-strategy.md) — overall SEO direction, keyword tiers, and what we stop doing.
- [`referral-loops.md`](referral-loops.md) — referral program tuning, viral coefficients worth testing, share-the-transcript loop ideas.
- [`pricing-experiments.md`](pricing-experiments.md) — price tests, annual-plan positioning, free-tier calibration.
- [`activation-retention.md`](activation-retention.md) — first-run experience, aha-moment, win-back flows.

## How to use this folder

- Proposing a new experiment? Add it to the matching doc with: **hypothesis**, **how we'd know it worked**, **how we'd know it failed**, **cost to try**.
- Killing something? Move it to a `## Killed` section with the reason. We keep the gravestones so we don't rerun the same experiment in six months.
- Shipping something? Leave the doc entry intact, add a `**Shipped:** YYYY-MM-DD — commit abc1234` line so future-us can trace what made it to prod.
