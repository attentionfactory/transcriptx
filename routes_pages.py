import json
from datetime import datetime
from flask import render_template
from seo_catalog import (
    COMPARISON_PAGES,
    CURATED_PLATFORM_OVERRIDES,
    GUIDE_TOOL_MAP,
    HEAD_TERM_PAGES,
    HELP_PAGES,
    PERSONA_PAGES,
    PLATFORM_CATEGORIES,
    RESEARCH_PAGES,
    current_lastmod,
    get_platform_pages,
    get_platforms_by_category,
)


def _format_last_updated(iso_date):
    """Convert ISO (YYYY-MM-DD) to human-readable ('23 Apr 2026')."""
    try:
        return datetime.strptime(iso_date, "%Y-%m-%d").strftime("%d %b %Y")
    except (ValueError, TypeError):
        return iso_date or ""


def _build_platform_index_html(platform_pages):
    """Render the 1000+ supported platforms as a searchable HTML table.

    Groups pages alphabetically and wraps in a client-side filter input. Kept in
    this module (not the template) so the existing research.html stays generic.
    """
    from html import escape as h

    rows = sorted(platform_pages.values(), key=lambda p: p.get("display_name", "").lower())
    total = len(rows)

    # Group into A-Z buckets plus "0-9 / other".
    buckets = {}
    for page in rows:
        name = (page.get("display_name") or "").strip()
        if not name:
            continue
        first = name[0].upper()
        key = first if first.isalpha() else "0-9"
        buckets.setdefault(key, []).append(page)

    letters = sorted(k for k in buckets if k != "0-9")
    if "0-9" in buckets:
        letters.append("0-9")

    parts = []
    parts.append(
        '<div class="platform-index-wrap" style="background:rgba(255,255,255,0.22);'
        'padding:1.2rem 1.4rem;border-radius:14px;margin:1rem 0;">'
    )
    parts.append(
        f'<p style="font-size:.85rem;opacity:.9;margin-bottom:1rem;">'
        f"<strong>{total:,} sites and counting.</strong> Not sure if yours is on the list? "
        f"Search below. And even if you don't find it, paste the link anyway — we can "
        f"often handle sites we haven't officially listed.</p>"
    )
    parts.append(
        '<input type="text" id="platform-filter" placeholder="Filter — type a platform name..." '
        'oninput="filterPlatforms()" '
        'style="width:100%;padding:.7rem 1rem;font-family:inherit;font-size:.8rem;'
        'border:var(--bw) solid rgba(0,0,0,.3);border-radius:8px;'
        'background:rgba(255,255,255,.5);margin-bottom:1rem;">'
    )
    parts.append(
        '<div class="platform-letter-nav" style="display:flex;gap:4px;flex-wrap:wrap;'
        'margin-bottom:1rem;font-size:.7rem;">'
    )
    for L in letters:
        parts.append(
            f'<a href="#letter-{h(L)}" style="padding:.25rem .45rem;border:var(--bw) solid '
            f'rgba(0,0,0,.25);border-radius:4px;text-decoration:none;color:var(--ink);'
            f'background:rgba(255,255,255,.4);">{h(L)}</a>'
        )
    parts.append("</div>")
    parts.append('<div id="platform-sections">')
    for L in letters:
        entries = buckets[L]
        parts.append(
            f'<section class="platform-letter-section" data-letter="{h(L)}" '
            f'id="letter-{h(L)}" style="margin-top:1.4rem;">'
        )
        parts.append(
            f'<h3 style="font-family:var(--f-wide);font-size:.9rem;text-transform:uppercase;'
            f'margin-bottom:.5rem;border-bottom:var(--bw) solid rgba(0,0,0,.25);'
            f'padding-bottom:.25rem;">{h(L)}</h3>'
        )
        parts.append(
            '<ul class="platform-list" style="list-style:none;padding:0;'
            'display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));'
            'gap:.25rem .8rem;margin:0;">'
        )
        for page in entries:
            name = h(page.get("display_name") or page.get("slug", ""))
            path = h(page.get("path", "#"))
            slug = h(page.get("slug", ""))
            parts.append(
                f'<li class="platform-item" data-name="{name.lower()}" '
                f'data-slug="{slug}" style="font-size:.78rem;padding:.2rem 0;">'
                f'<a href="{path}" style="color:var(--ink);text-decoration:none;">{name}</a>'
                f'</li>'
            )
        parts.append("</ul>")
        parts.append("</section>")
    parts.append("</div>")
    parts.append("""
<script>
(function(){
  var input = document.getElementById('platform-filter');
  if (!input) return;
  window.filterPlatforms = function(){
    var q = (input.value || '').trim().toLowerCase();
    var items = document.querySelectorAll('.platform-item');
    var sections = document.querySelectorAll('.platform-letter-section');
    if (!q) {
      items.forEach(function(el){ el.style.display=''; });
      sections.forEach(function(s){ s.style.display=''; });
      return;
    }
    sections.forEach(function(s){
      var anyVisible = false;
      s.querySelectorAll('.platform-item').forEach(function(el){
        var match = (el.dataset.name || '').indexOf(q) !== -1 ||
                    (el.dataset.slug || '').indexOf(q) !== -1;
        el.style.display = match ? '' : 'none';
        if (match) anyVisible = true;
      });
      s.style.display = anyVisible ? '' : 'none';
    });
  };
})();
</script>
""")
    parts.append("</div>")

    # Add context around the index.
    preamble = """
<h2>How to use this</h2>
<p>If you're wondering whether we can transcribe a video from a specific site, check here first. The list below stays in sync with what we actually support — when we add a new site, it shows up automatically.</p>
<p>Each site name links to its own page with a bit more detail, in case you want to read up before pasting a link.</p>
<h2>Where most people actually transcribe from</h2>
<p>The list is long, but most of the time people are pulling videos from 8 or 9 familiar spots: YouTube, TikTok, Instagram, X (Twitter), Facebook, Reddit, Vimeo, LinkedIn, Twitch, SoundCloud. The rest is the long list of everything else — regional news, niche streaming, educational sites, and so on — so you've got options when the video you need isn't on a mainstream site.</p>
"""

    appendix = """
<h2>Don't see your site?</h2>
<p>A few things to try:</p>
<ul>
<li><strong>Paste the link anyway.</strong> We can often handle sites we haven't officially listed. If the video plays in a normal browser without a login, there's a good chance it'll work.</li>
<li><strong>Is it behind a login?</strong> Discord calls, private Zoom rooms, internal Slack — we can't reach those without being logged in. <a href="/help/private-video-transcript">Here's the workaround</a>.</li>
<li><strong>Is it a brand-new site?</strong> We add new ones fairly regularly. Email us with the site you need and we'll take a look.</li>
<li><strong>Some enterprise video tools are funny.</strong> Panopto, Kaltura, Brightcove — we support them, but you need the link to the viewer page (the one where you watch), not the raw media URL.</li>
</ul>
<h2>Also worth a look</h2>
<ul>
<li><a href="/compare/best-youtube-transcript-tools">How we compare to other transcript tools</a></li>
<li><a href="/help">Help &amp; troubleshooting</a> — if something's not working, the fix is probably here</li>
<li><a href="/research/transcription-accuracy-benchmark">How accurate is this really?</a> — honest numbers against 4 other tools</li>
</ul>
"""

    return preamble + "".join(parts) + appendix


def register_page_routes(
    app,
    *,
    get_current_user,
    get_banner,
    checkout_starter,
    checkout_pro,
    customer_portal,
    featurebase_app_id,
    guides_content,
    checkout_starter_annual=None,
    checkout_pro_annual=None,
):
    # Annual checkout URLs fall back to monthly until the annual products are
    # configured in Polar. Pricing toggle shows the same CTA for both states
    # until annual URLs are distinct.
    checkout_starter_annual = checkout_starter_annual or checkout_starter
    checkout_pro_annual = checkout_pro_annual or checkout_pro
    def _tool_schema(page, canonical_url):
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": page["h1"],
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web",
            "url": canonical_url,
            "description": page["description"],
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        }

    def _faq_schema(page):
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": row["q"],
                    "acceptedAnswer": {"@type": "Answer", "text": row["a"]},
                }
                for row in page.get("faq", [])
            ],
        }

    def _platform_sections(page):
        platform = page.get("display_name") or page.get("platform") or "this platform"
        intro = page.get("intro") or page.get("description") or ""
        return [
            {
                "title": f"How {platform} transcript extraction works",
                "body": intro,
            },
            {
                "title": "What you can do with the transcript",
                "body": (
                    "Extract searchable text, capture timestamped quotes, and repurpose "
                    "video/audio into docs, briefs, posts, and editorial workflows."
                ),
            },
        ]

    def _seo_sections(page):
        platform = page.get("platform") or page.get("display_name") or "video"
        intro = page.get("intro") or page.get("description") or ""
        keyword = page.get("keyword") or page.get("h1") or "transcript extraction"
        return [
            {
                "title": f"What this {keyword} page is for",
                "body": intro,
            },
            {
                "title": f"Why teams use TranscriptX for {platform}",
                "body": (
                    "Use one URL-to-text workflow to extract accurate transcripts, preserve "
                    "timestamps, and repurpose spoken content into publish-ready assets."
                ),
            },
        ]

    def _platform_robots(slug):
        # Keep high-intent curated platforms indexable; long-tail programmatic pages stay discoverable via links/sitemap but noindexed by default.
        if slug in CURATED_PLATFORM_OVERRIDES:
            return "index,follow"
        return "noindex,follow"

    def _platform_related_links(page):
        platform = (page.get("display_name") or page.get("platform") or "").lower()
        primary = "/youtube-transcript-generator" if "youtube" in platform else "/video-to-transcript"
        return [
            {"href": primary, "label": "Main transcript workflow"},
            {"href": "/research/platform-support-index", "label": "Sites we support"},
            {"href": "/compare/best-youtube-transcript-tools", "label": "Tool comparison"},
        ]

    @app.route("/v2")
    def v2_landing():
        user = get_current_user()
        return render_template(
            "v2.html",
            user=user,
            banner=get_banner(),
            config={
                "checkout_starter": checkout_starter,
                "checkout_pro": checkout_pro,
                "customer_portal": customer_portal,
            },
        )

    @app.route("/v3")
    def v3_landing():
        user = get_current_user()
        return render_template(
            "v3.html",
            user=user,
            banner=get_banner(),
            config={
                "checkout_starter": checkout_starter,
                "checkout_pro": checkout_pro,
                "customer_portal": customer_portal,
            },
        )

    @app.route("/")
    def index():
        from database import get_total_transcript_count
        user = get_current_user()
        return render_template(
            "index.html",
            user=user,
            banner=get_banner(),
            total_transcripts=get_total_transcript_count(),
            config={
                "checkout_starter": checkout_starter,
                "checkout_pro": checkout_pro,
                "customer_portal": customer_portal,
                "featurebase_app_id": featurebase_app_id,
            },
        )

    @app.route("/pricing")
    def pricing():
        user = get_current_user()
        return render_template(
            "pricing.html",
            user=user,
            config={
                "checkout_starter": checkout_starter,
                "checkout_pro": checkout_pro,
                "checkout_starter_annual": checkout_starter_annual,
                "checkout_pro_annual": checkout_pro_annual,
                "customer_portal": customer_portal,
                "featurebase_app_id": featurebase_app_id,
            },
        )

    @app.route("/profile-links")
    def profile_links():
        user = get_current_user()
        return render_template(
            "profile_links.html",
            user=user,
            banner=get_banner(),
            config={
                "checkout_starter": checkout_starter,
                "checkout_pro": checkout_pro,
                "customer_portal": customer_portal,
                "featurebase_app_id": featurebase_app_id,
            },
        )

    @app.route("/guides")
    def guides_index():
        guides = [
            {"slug": slug, "title": guide["title"], "description": guide["description"]}
            for slug, guide in guides_content.items()
        ]
        return render_template("guides_index.html", guides=guides)

    @app.route("/guides/<slug>")
    def guide_page(slug):
        guide = guides_content.get(slug)
        if not guide:
            return ("Guide not found", 404)

        last_updated_iso = current_lastmod()
        last_updated_display = _format_last_updated(last_updated_iso)

        article_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": guide["title"],
            "description": guide["description"],
            "author": {"@type": "Organization", "name": "TranscriptX"},
            "publisher": {"@type": "Organization", "name": "TranscriptX"},
            "mainEntityOfPage": f"https://transcriptx.xyz/guides/{slug}",
            "datePublished": last_updated_iso,
            "dateModified": last_updated_iso,
        }
        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item["q"],
                    "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
                }
                for item in guide["faq"]
            ],
        }

        return render_template(
            "guide.html",
            guide=guide,
            slug=slug,
            primary_tool_path=GUIDE_TOOL_MAP.get(slug, "/youtube-transcript-generator"),
            article_schema_json=json.dumps(article_schema),
            faq_schema_json=json.dumps(faq_schema),
            last_updated=last_updated_display,
        )

    for page in HEAD_TERM_PAGES.values():
        endpoint = f"seo_head_{page['slug'].replace('-', '_')}"

        def _make_head_handler(page_data):
            def _handler():
                canonical_url = f"https://transcriptx.xyz{page_data['path']}"
                return render_template(
                    "index.html",
                    user=get_current_user(),
                    banner=get_banner(),
                    config={
                        "checkout_starter": checkout_starter,
                        "checkout_pro": checkout_pro,
                        "customer_portal": customer_portal,
                        "featurebase_app_id": featurebase_app_id,
                    },
                    seo_title=page_data.get("title"),
                    seo_description=page_data.get("description"),
                    app_schema_json=json.dumps(_tool_schema(page_data, canonical_url)),
                    faq_schema_json=json.dumps(_faq_schema(page_data)),
                    canonical_url=canonical_url,
                    hero_h1=page_data.get("h1"),
                    hero_intro=page_data.get("intro") or page_data.get("description"),
                    hero_label=page_data.get("cta_hint") or "Initialize Transcription",
                    cta_label=page_data.get("cta_label") or "Extract Transcript",
                    seo_text_sections=_seo_sections(page_data),
                    seo_faq_items=page_data.get("faq") or [],
                )

            return _handler

        app.add_url_rule(page["path"], endpoint, _make_head_handler(page))

    @app.route("/platform/<slug>-transcript-generator")
    def platform_landing(slug):
        page = get_platform_pages().get(slug)
        if not page:
            return ("Platform not found", 404)
        canonical_url = f"https://transcriptx.xyz{page['path']}"
        return render_template(
            "index.html",
            user=get_current_user(),
            banner=get_banner(),
            config={
                "checkout_starter": checkout_starter,
                "checkout_pro": checkout_pro,
                "customer_portal": customer_portal,
                "featurebase_app_id": featurebase_app_id,
            },
            seo_title=page.get("title"),
            seo_description=page.get("description"),
            app_schema_json=json.dumps(_tool_schema(page, canonical_url)),
            faq_schema_json=json.dumps(_faq_schema(page)),
            canonical_url=canonical_url,
            hero_h1=page.get("h1"),
            hero_intro=page.get("intro") or page.get("description"),
            hero_label=page.get("cta_hint") or "Initialize Transcription",
            cta_label=page.get("cta_label") or "Extract Transcript",
            seo_text_sections=_platform_sections(page),
            seo_faq_items=page.get("faq") or [],
            seo_related_links=_platform_related_links(page),
            seo_robots=_platform_robots(slug),
        )

    @app.route("/compare/<slug>")
    def compare_page(slug):
        page = COMPARISON_PAGES.get(slug)
        if not page:
            return ("Comparison not found", 404)
        canonical_url = f"https://transcriptx.xyz/compare/{slug}"
        return render_template(
            "compare.html",
            page=page,
            canonical_url=canonical_url,
            faq_schema_json=json.dumps(_faq_schema(page)),
            last_updated=_format_last_updated(current_lastmod()),
        )

    @app.route("/research/<slug>")
    def research_page(slug):
        page = RESEARCH_PAGES.get(slug)
        if not page:
            return ("Research page not found", 404)
        canonical_url = f"https://transcriptx.xyz/research/{slug}"

        # Special case: platform-support-index renders the live list of platforms.
        # We build the body HTML here so the catalog entry stays small and the
        # data source (get_platform_pages) stays the single source of truth.
        if slug == "platform-support-index":
            page = dict(page)
            page["body_html"] = _build_platform_index_html(get_platform_pages())

        last_updated_iso = current_lastmod()
        return render_template(
            "research.html",
            page=page,
            canonical_url=canonical_url,
            last_updated=_format_last_updated(last_updated_iso),
            faq_schema_json=json.dumps(_faq_schema(page)) if page.get("faq") else None,
        )

    @app.route("/help")
    def help_index():
        return render_template(
            "help_index.html",
            articles=HELP_PAGES,
        )

    @app.route("/help/<slug>")
    def help_page(slug):
        page = HELP_PAGES.get(slug)
        if not page:
            return ("Help article not found", 404)
        canonical_url = f"https://transcriptx.xyz/help/{slug}"
        last_updated_iso = current_lastmod()

        article_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": page["title"],
            "description": page["meta_description"],
            "author": {"@type": "Organization", "name": "TranscriptX"},
            "publisher": {"@type": "Organization", "name": "TranscriptX"},
            "mainEntityOfPage": canonical_url,
            "datePublished": last_updated_iso,
            "dateModified": last_updated_iso,
        }

        return render_template(
            "help.html",
            page=page,
            canonical_url=canonical_url,
            article_schema_json=json.dumps(article_schema),
            faq_schema_json=json.dumps(_faq_schema(page)) if page.get("faq") else None,
            last_updated=_format_last_updated(last_updated_iso),
        )

    @app.route("/for/<slug>")
    def persona_page(slug):
        page = PERSONA_PAGES.get(slug)
        if not page:
            return ("Persona page not found", 404)
        canonical_url = f"https://transcriptx.xyz/for/{slug}"
        last_updated_iso = current_lastmod()

        article_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": page["title"],
            "description": page["meta_description"],
            "author": {"@type": "Organization", "name": "TranscriptX"},
            "publisher": {"@type": "Organization", "name": "TranscriptX"},
            "mainEntityOfPage": canonical_url,
            "datePublished": last_updated_iso,
            "dateModified": last_updated_iso,
        }

        return render_template(
            "persona.html",
            page=page,
            canonical_url=canonical_url,
            article_schema_json=json.dumps(article_schema),
            faq_schema_json=json.dumps(_faq_schema(page)) if page.get("faq") else None,
            last_updated=_format_last_updated(last_updated_iso),
        )

    @app.route("/categories")
    def categories_index():
        # Pre-compute platform counts per category so the index can show them.
        counts = {slug: len(get_platforms_by_category(slug)) for slug in PLATFORM_CATEGORIES}
        return render_template(
            "categories_index.html",
            categories=PLATFORM_CATEGORIES,
            counts=counts,
        )

    @app.route("/category/<slug>")
    def category_page(slug):
        category = PLATFORM_CATEGORIES.get(slug)
        if not category:
            return ("Category not found", 404)
        platforms = get_platforms_by_category(slug)
        canonical_url = f"https://transcriptx.xyz/category/{slug}"
        return render_template(
            "category.html",
            category=category,
            platforms=platforms,
            canonical_url=canonical_url,
            last_updated=_format_last_updated(current_lastmod()),
        )

    @app.route("/press-kit")
    def press_kit_page():
        return render_template(
            "press_kit.html",
            canonical_url="https://transcriptx.xyz/press-kit",
            comparison_pages=COMPARISON_PAGES,
            research_pages=RESEARCH_PAGES,
        )
