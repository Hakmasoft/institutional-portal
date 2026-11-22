from .base import *  # noqa: F401,F403

DEBUG = False

# --- Hosts -------------------------------------------------------------
# Render injects RENDER_EXTERNAL_HOSTNAME at build/runtime.
RENDER_HOSTNAME = env("RENDER_EXTERNAL_HOSTNAME", default="")  # noqa: F405
if RENDER_HOSTNAME:
    ALLOWED_HOSTS = list(ALLOWED_HOSTS) + [RENDER_HOSTNAME]  # noqa: F405

# --- Database ----------------------------------------------------------
DATABASES = {
    "default": env.db("DATABASE_URL"),  # noqa: F405
}
DATABASES["default"]["CONN_MAX_AGE"] = 60

DATABASES["default"].setdefault("OPTIONS", {})
DATABASES["default"]["OPTIONS"]["sslmode"] = "require"

# --- Static files (WhiteNoise) ----------------------------------------
# Must be inserted right after SecurityMiddleware (index 1).
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --- HTTPS / security headers -----------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)  # noqa: F405

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS deliberately 0 until the human verifies the deploy. Raise later.
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=0)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# --- CSRF -------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = env.list(  # noqa: F405
    "DJANGO_CSRF_TRUSTED_ORIGINS", default=[]
)
if RENDER_HOSTNAME:
    CSRF_TRUSTED_ORIGINS = list(CSRF_TRUSTED_ORIGINS) + [
        f"https://{RENDER_HOSTNAME}"
    ]
