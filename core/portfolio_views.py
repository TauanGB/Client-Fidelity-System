"""Serve only the public, synthetic portfolio files, without template context."""

from pathlib import Path

from django.http import FileResponse, Http404
from django.views import View


PORTFOLIO_ROOT = Path(__file__).resolve().parent.parent / "portfolio"
PUBLIC_FILES = {
    "index.html": "text/html; charset=utf-8",
    "styles.css": "text/css; charset=utf-8",
    "app.js": "text/javascript; charset=utf-8",
    "favicon.svg": "image/svg+xml",
}


class PortfolioView(View):
    asset = "index.html"
    http_method_names = ["get", "head", "options"]

    def get(self, request, *args, **kwargs):
        # The route supplies this value; never accept a filesystem path from a URL.
        if self.asset not in PUBLIC_FILES:
            raise Http404("Portfolio asset not found.")
        try:
            file = (PORTFOLIO_ROOT / self.asset).open("rb")
        except FileNotFoundError as exc:
            raise Http404("Portfolio asset not found.") from exc
        return FileResponse(file, content_type=PUBLIC_FILES[self.asset])
