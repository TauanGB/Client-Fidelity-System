from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from django.http import Http404
from django.test import RequestFactory, SimpleTestCase
from django.urls import resolve, reverse

from .portfolio_views import PortfolioView


PORTFOLIO = Path(__file__).resolve().parent.parent / "portfolio"


class PortfolioHomeTests(SimpleTestCase):
    """No database access is allowed, including for the public home page."""

    def read_response(self, response):
        try:
            return b"".join(response.streaming_content)
        finally:
            response.close()

    def test_root_returns_exact_standalone_landing_without_redirect(self):
        self.assertEqual(reverse("core:home"), "/")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")
        self.assertEqual(self.read_response(response), (PORTFOLIO / "index.html").read_bytes())

    def test_authenticated_user_also_sees_landing(self):
        request = RequestFactory().get("/")
        request.user = SimpleNamespace(is_authenticated=True)
        response = resolve("/").func(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Fidelity", self.read_response(response))

    def test_all_relative_assets_are_served_with_correct_content_types(self):
        for route, filename, content_type in [
            ("core:portfolio-styles", "styles.css", "text/css; charset=utf-8"),
            ("core:portfolio-script", "app.js", "text/javascript; charset=utf-8"),
            ("core:portfolio-favicon", "favicon.svg", "image/svg+xml"),
        ]:
            with self.subTest(asset=filename):
                response = self.client.get(reverse(route))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], content_type)
                self.assertEqual(self.read_response(response), (PORTFOLIO / filename).read_bytes())

    def test_head_returns_headers_without_body(self):
        response = self.client.head("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response["Content-Length"]), (PORTFOLIO / "index.html").stat().st_size)
        self.assertEqual(self.read_response(response), b"")

    def test_post_does_not_change_anything(self):
        self.assertEqual(self.client.post("/").status_code, 405)

    def test_unlisted_files_and_traversal_are_not_exposed(self):
        for path in ["/README.md", "/manage.py", "/portfolio/manage.py", "/../manage.py"]:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)

    def test_view_rejects_unlisted_file_even_if_misconfigured(self):
        with self.assertRaises(Http404):
            PortfolioView.as_view(asset="../manage.py")(RequestFactory().get("/"))

    def test_missing_public_file_returns_404(self):
        with patch("core.portfolio_views.Path.open", side_effect=FileNotFoundError):
            self.assertEqual(self.client.get("/").status_code, 404)

    def test_dashboard_still_requires_authentication(self):
        request = RequestFactory().get(reverse("core:dashboard"))
        request.user = SimpleNamespace(is_authenticated=False)
        response = resolve(request.path).func(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("accounts:login") + "?next=/dashboard/")

    def test_login_and_dashboard_routes_are_preserved(self):
        self.assertEqual(reverse("accounts:login"), "/accounts/login/")
        self.assertEqual(reverse("core:dashboard"), "/dashboard/")
