# Session Snapshot — 2026-04-23

Pick-up doc for continuing this work in a new agent window. Reads cold.

## Where the code is

- **Branch:** `staging` (pushed, up to date with origin).
- **Last 4 commits on staging:**
  - `9f429eb` — friction-points doc (19 items, 3 themes, 4-week plan)
  - `d758e40` — Growth docs folder scaffolding (6 files)
  - `f42bde6` — plain-English sweep for guides (GUIDES_CONTENT in app.py)
  - `eb00eab` — plain-English sweep for SEO pages (seo_catalog.py + templates)
- **Uncommitted:** none. `templates/v2.html` and `templates/v3.html` are local scratch files — per memory, do not commit.

## What this session was about

User called out that the SEO content sounded like it was "written for dev people" — phrases like *platform index*, *URL paste*, *long-tail*, *mid-funnel*, *compounds*. Directed a rewrite to sound human ("Bring videos from anywhere" kind of voice).

That triggered three waves of work:
1. **Language sweep** across all SEO copy, comparison pages, help pages, category pages, the platform support index, and the in-product guides.
2. **Growth docs** scaffolding — a working notebook in `docs/growth/` (never served by Flask) for SEO/content/referral/pricing/retention thinking.
3. **Friction-point analysis** — auditing the product through the lens "every guide we have to write is a missing feature".

## The docs that now exist in `docs/growth/`

Read in this order:

1. [`README.md`](README.md) — operating principles (solve specific Googled problems, lead with 60-second answer, ship-measure-kill).
2. [`friction-points.md`](friction-points.md) — **this is the most actionable doc.** 19 friction points from error messages and help pages, grouped by severity, with a 4-week prioritized fix plan and kill criteria.
3. [`content-guides-backlog.md`](content-guides-backlog.md) — 25 guide topics ranked in 3 tiers. Each one solves a specific Google query. Replaces the SEO-fluff guides currently in `GUIDES_CONTENT`.
4. [`seo-strategy.md`](seo-strategy.md) — keyword tiers A-D, what we stop doing, internal linking rules.
5. [`referral-loops.md`](referral-loops.md) — 5 experiments (share-the-transcript, 2-tier, gifting, embed badge, paid kickback).
6. [`pricing-experiments.md`](pricing-experiments.md) — lifetime deal, usage-based, student, Pro+, free-tier calibration.
7. [`activation-retention.md`](activation-retention.md) — instant preview, reactivation email, history dashboard, aha-moment definition.

Every experiment across every doc has **hypothesis / worked / failed / cost to try**. That's the house style; keep it.

## The three insights from the friction audit (don't lose these)

1. **URL-only is a shared root cause.** F1, F4, F6, F11, F15 in [friction-points.md](friction-points.md) all share it. Accepting file upload unblocks roughly 40% of the guide backlog at once.
2. **Errors leak raw exceptions and dead-end CTAs.** [app.py:657](../../app.py), [app.py:670](../../app.py), [app.py:817](../../app.py), [app.py:566](../../app.py) all do `str(e)` or "try again later" with no retry time, no upgrade link, no recovery action. Half the friction items collapse to one fix: a unified error classifier.
3. **Activation works; retention has no system.** Free-tier resets are silent. No transcript history. No return trigger. See [activation-retention.md](activation-retention.md).

## Recommended next 4 weeks (from friction doc)

1. **Week 1 — Error classifier (F5).** Touches half the friction items. Low eng cost.
2. **Week 2 — Language-retry UI surfacing (F8).** Feature already exists at [app.py:740](../../app.py) `/api/retranscribe`; just needs inline UI promotion on the result screen.
3. **Week 3 — File upload, Pro-flagged (F1).** Biggest single guide-backlog unlock. Pro-flag to cap infra spend while we measure.
4. **Week 4 — Structured upgrade error (F3).** Direct revenue impact. Return `{error, upgrade_url, current_credits, suggested_plan}` instead of bare text.

Each has a kill criterion in the doc — honor them.

## What the user is thinking about next

The user mentioned wanting to do an SEO Quick Audit at some point. Not yet scoped — bring it up if they don't.

Also open: choosing which of the 25 backlog guides to write first. The top-5 highest-leverage per the backlog doc: #1 Google Drive, #6 Loom, #8 Microsoft Teams, #14 Language/translate, #21 iPhone. All five solve problems the user can't easily fix elsewhere and have unambiguous search intent.

## Voice / style rules the user cares about

Hard-learned in this session:

- **Write like a smart friend explaining, not a marketer or dev.** No *mid-funnel*, *compounds*, *topical authority*, *content velocity*, *ICP*, *URL-based*, *platform breadth*.
- **H1 = the exact problem the user Googled.** Not cute, not clever.
- **60-second answer up front.** Before any preamble.
- **Honest about limitations.** Instagram Stories are hard; say so. Spotify isn't supported; say so. Honesty converts better than hedging.
- **The only template file that ships is `templates/index.html`.** `v2.html` / `v3.html` are scratch.

## Repo facts worth knowing

- **Stack:** Flask + Jinja2, Python 3. Run with `python3` (no `python` on this machine).
- **Billing:** Polar (prior session work).
- **Key files for content edits:**
  - `seo_catalog.py` — HEAD_TERM_PAGES, COMPARISON_PAGES, HELP_PAGES, RESEARCH_PAGES, PERSONA_PAGES, PLATFORM_CATEGORIES.
  - `app.py` — contains `GUIDES_CONTENT` starting at line 2276. Also all error messages and API routes.
  - `routes_pages.py` — includes `_build_platform_index_html()` which renders the live platforms list.
  - `templates/index.html` — the live homepage / product UI.
- **Live pages user cares about:** `/categories`, `/research/platform-support-index`, `/guides/<slug>`, `/compare/<slug>`.

## What to do first in the next session

Ask the user: **which of the three levers next — (a) start writing the Tier-1 guides, (b) start fixing the friction points, (c) SEO quick audit?** Don't assume; they've been jumping between strategic and tactical work in this session and may want any of the three.

If they say "just keep going" or similar, default to **(b) friction Week 1 — error classifier** — it's the highest ROI and doesn't require any design decisions to start.
