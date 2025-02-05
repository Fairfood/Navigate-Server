from .base import *  # noqa
from .base import BASE_DIR
from .base import REST_FRAMEWORK

DEBUG = True

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = ["http://localhost:8000"]

STATIC_ROOT = BASE_DIR.parent / "app" / "static"

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["anon"] = "500/min"

HUB_TOPIC_ID = "0.0.47654162"

# PYINSTRUMENT_PROFILE_DIR = "profiles"
# ENABLE_PROFILING = False
# if ENABLE_PROFILING:
#     MIDDLEWARE += ["pyinstrument.middleware.ProfilerMiddleware"]

AWS_DEFAULT_REGION = "eu-central-1"
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""