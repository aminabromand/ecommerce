# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Let's Encrypt ssl/tls https
CORS_REPLACE_HTTPS_REFERER      = False
HOST_SCHEME                     = 'http://'
SECURE_PROXY_SSL_HEADER         = None
SECURE_SSL_REDIRECT             = False
SESSION_COOKIE_SECURE           = False
CSRF_COOKIE_SECURE              = False
SECURE_HSTS_INCLUDE_SUBDOMAINS  = False
SECURE_HSTS_SECONDS             = None
SECURE_FRAME_DENY               = False
