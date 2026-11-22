from .base import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    "default": env.db("DATABASE_URL"),  # noqa: F405
}

# TODO Task 2: WhiteNoise, security headers, CSRF_TRUSTED_ORIGINS, gunicorn
