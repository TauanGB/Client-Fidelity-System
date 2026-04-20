import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent.parent


def env(name, default=None):
    return os.environ.get(name, default)


def env_bool(name, default=False):
    value = env(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default=""):
    raw_value = env(name, default)
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def env_int(name, default=0):
    value = env(name)
    if value is None:
        return default
    return int(value)


def database_config():
    database_url = env("DATABASE_URL")
    if not database_url:
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }

    parsed = urlparse(database_url)
    query = parse_qs(parsed.query)
    engine_map = {
        "postgres": "django.db.backends.postgresql",
        "postgresql": "django.db.backends.postgresql",
        "pgsql": "django.db.backends.postgresql",
        "sqlite": "django.db.backends.sqlite3",
    }
    engine = engine_map.get(parsed.scheme)
    if not engine:
        raise ValueError(f"Unsupported DATABASE_URL scheme: {parsed.scheme}")

    if engine == "django.db.backends.sqlite3":
        sqlite_path = parsed.path[1:] if parsed.path.startswith("/") else parsed.path
        return {
            "ENGINE": engine,
            "NAME": sqlite_path or BASE_DIR / "db.sqlite3",
        }

    return {
        "ENGINE": engine,
        "NAME": parsed.path.lstrip("/"),
        "USER": parsed.username or "",
        "PASSWORD": parsed.password or "",
        "HOST": parsed.hostname or "",
        "PORT": parsed.port or "",
        "CONN_MAX_AGE": int(env("DB_CONN_MAX_AGE", "60")),
        "OPTIONS": {key: values[0] for key, values in query.items() if values},
    }


SECRET_KEY = env("SECRET_KEY", "django-insecure-change-me")
DEBUG = env_bool("DEBUG", default=True)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "")

if not DEBUG:
    if SECRET_KEY == "django-insecure-change-me":
        raise ValueError("SECRET_KEY must be configured for production.")
    if not ALLOWED_HOSTS:
        raise ValueError("ALLOWED_HOSTS must be configured when DEBUG=False.")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
    "core",
    "accounts",
    "company",
    "loyalty",
    "customers",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "fidelity_system.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "company.context_processors.company_branding",
            ],
        },
    },
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

WSGI_APPLICATION = "fidelity_system.wsgi.application"

DATABASES = {
    "default": database_config(),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = env("TIME_ZONE", "America/Sao_Paulo")
USE_I18N = True
USE_TZ = True

STATIC_URL = env("STATIC_URL", "/static/")
STATIC_ROOT = Path(env("STATIC_ROOT", str(BASE_DIR / "staticfiles")))
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
WHITENOISE_MAX_AGE = env_int("WHITENOISE_MAX_AGE", default=60 if DEBUG else 31536000)

MEDIA_URL = env("MEDIA_URL", "/media/")
MEDIA_ROOT = Path(env("MEDIA_ROOT", str(BASE_DIR / "media")))

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "accounts:login"

SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", default=not DEBUG)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = env_bool("CSRF_COOKIE_HTTPONLY", default=False)
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", default=not DEBUG)
SECURE_HSTS_SECONDS = env_int("SECURE_HSTS_SECONDS", default=0 if DEBUG else 31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=not DEBUG)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", default=False)
SECURE_CONTENT_TYPE_NOSNIFF = env_bool("SECURE_CONTENT_TYPE_NOSNIFF", default=True)
SECURE_REFERRER_POLICY = env("SECURE_REFERRER_POLICY", "same-origin")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") if env_bool("USE_X_FORWARDED_PROTO", default=not DEBUG) else None

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
