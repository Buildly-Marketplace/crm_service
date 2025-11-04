from .base import *

ALLOWED_HOSTS = [
    os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
]

if os.getenv('CORS_ORIGIN_ALLOW_ALL') == 'True':
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CORS_ORIGIN_WHITELIST = os.getenv('CORS_ORIGIN_WHITELIST', 'localhost,127.0.0.1').split(',')

# Redis support
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')