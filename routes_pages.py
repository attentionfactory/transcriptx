import json
from flask import render_template


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
):
    @app.route("/")
    def index():
        user = get_current_user()
        return render_template(
            "index.html",
            user=user,
            banner=get_banner(),
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

        article_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": guide["title"],
            "description": guide["description"],
            "author": {"@type": "Organization", "name": "TranscriptX"},
            "publisher": {"@type": "Organization", "name": "TranscriptX"},
            "mainEntityOfPage": f"https://transcriptx.xyz/guides/{slug}",
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
            article_schema_json=json.dumps(article_schema),
            faq_schema_json=json.dumps(faq_schema),
        )
