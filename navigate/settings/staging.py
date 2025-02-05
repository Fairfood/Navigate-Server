from datetime import timedelta

from .base import *  # noqa
from .base import REST_FRAMEWORK, env

DEBUG = True

ALLOWED_HOSTS = [
    DOMAIN_NAME
]

CORS_ORIGIN_WHITELIST = (BASE_URL,)


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
DEFAULT_S3_PATH = "navigate"
MEDIA_ROOT = "/%s/" % DEFAULT_S3_PATH
MEDIA_URL = "//%s.s3.amazonaws.com/navigate/" % AWS_STORAGE_BUCKET_NAME

# SENTRY SETUP AWS_STORAGE_BUCKET_NAME:
