import json
from datetime import datetime
from flask import render_template
from seo_catalog import (
    COMPARISON_PAGES,
    CURATED_PLATFORM_OVERRIDES,
    GUIDE_TOOL_MAP,
    HEAD_TERM_PAGES,
    HELP_PAGES,
    RESEARCH_PAGES,
    current_lastmod,
    get_platform_pages,
)


def _format_last_updated(iso_date):
    """Convert ISO (YYYY-MM-DD) to human-readable ('23 Apr 2026')."""
    try:
        return datetime.strptime(iso_date, "%Y-%m-%d").strftime("%d %b %Y")
    except (ValueError, TypeError):
        return iso_date or ""


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
            {"href": "/research/platform-support-index", "label": "Platform support index"},
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
        return render_template(
            "research.html",
            page=page,
            canonical_url=canonical_url,
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

    @app.route("/press-kit")
    def press_kit_page():
        return render_template(
            "press_kit.html",
            canonical_url="https://transcriptx.xyz/press-kit",
            comparison_pages=COMPARISON_PAGES,
            research_pages=RESEARCH_PAGES,
        )
