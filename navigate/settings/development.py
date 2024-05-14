from datetime import timedelta

from .base import *  # noqa
from .base import env
from .base import REST_FRAMEWORK


DEBUG = True

ALLOWED_HOSTS = [
    "v2.dev.api.fairfood.org",
]

CORS_ORIGIN_WHITELIST = ("https://v2.dev.api.fairfood.org",)


REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["anon"] = "500/min"


# Media file settings for S3

AWS_DEFAULT_REGION = "eu-central-1"
AWS_ACCESS_KEY_ID = env.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env.get("AWS_STORAGE_BUCKET_NAME")
AWS_QUERYSTRING_AUTH = False
AWS_PRELOAD_METADATA = True
AWS_DEFAULT_ACL = "public-read"
DEFAULT_FILE_STORAGE = "s3_folder_storage.s3.DefaultStorage"
DEFAULT_S3_PATH = "sso"
MEDIA_ROOT = "/%s/" % DEFAULT_S3_PATH
MEDIA_URL = "//%s.s3.amazonaws.com/sso/" % AWS_STORAGE_BUCKET_NAME

# SENTRY SETUP AWS_STORAGE_BUCKET_NAME:
