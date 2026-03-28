"""
Content Routes für Printly
"""

from flask import render_template, request
from flask_login import current_user
from ... import blueprint, app_logger, app_config, APP_NAME
from app.decorators import enabled_required
from app.config import Config
from ..page_config import PAGES, load_quote_calculator_context, load_dashboard_context
from ...models import PrintlyQuote

config = Config()
app_logger.info(f"Starte Content Routes für {APP_NAME}")


# ============================================================
# HELPER
# ============================================================


def is_ajax_request():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


# ============================================================
# INDEX
# ============================================================


@blueprint.route(f"/{APP_NAME}_index")
@blueprint.route("/")
@enabled_required
def Printly_index():
    extra_context = load_dashboard_context()
    return render_template(
        "Printly.html",
        user=current_user,
        config=config,
        content="dashboard",
        app_config=app_config,
        pages=PAGES,
        **extra_context,
    )


# ============================================================
# DYNAMISCHE ROUTEN
# ============================================================


def register_content_routes():
    for page in PAGES:

        def make_view(p):
            @blueprint.route(p["route"], methods=["GET"])
            @enabled_required
            def view_func():

                # Platzhalter → zurück zum Dashboard
                if p["placeholder"]:
                    return render_template(
                        "Printly.html",
                        user=current_user,
                        config=config,
                        content="dashboard",
                        app_config=app_config,
                        pages=PAGES,
                    )

                # Context aus loader holen
                extra_context = p["context_loader"]() if p.get("context_loader") else {}

                # AJAX → nur Fragment
                if is_ajax_request():
                    return render_template(
                        p["template"],
                        user=current_user,
                        config=config,
                        app_config=app_config,
                        **extra_context,
                    )

                # Normal → komplette Seite
                return render_template(
                    "Printly.html",
                    user=current_user,
                    config=config,
                    content=p["id"],
                    app_config=app_config,
                    pages=PAGES,
                    **extra_context,
                )

            view_func.__name__ = p["id"]
            return view_func

        make_view(page)


@blueprint.route("/quote/<int:quote_id>", endpoint="quote_detail_view")
@enabled_required
def quote_detail_view(quote_id):
    quote = PrintlyQuote.query.get_or_404(quote_id)
    context = load_quote_calculator_context()
    context["quote"] = quote

    if is_ajax_request():
        return render_template(
            "_custom/content/Quote_detail.html",
            user=current_user,
            config=config,
            app_config=app_config,
            **context,
        )

    return render_template(
        "Printly.html",
        user=current_user,
        config=config,
        content="quote_detail_page",
        app_config=app_config,
        pages=PAGES,
        **context,
    )


register_content_routes()
app_logger.info(f"Ende Content Routes für {APP_NAME}")
