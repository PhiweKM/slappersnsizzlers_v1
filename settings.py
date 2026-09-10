"""
Django settings for slappersnsizzlers_v1.

Reads its secrets and environment-specific values from a .env file (locally)
or real environment variables (on Render) via python-decouple, so the SAME
code runs in both places — the 12-factor rule: config lives in the
environment, never in the repo. Everything below the "PRODUCTION HARDENING"
banner switches on automatically when DEBUG=False.
"""
from pathlib import Path

import dj_database_url  # parses a DATABASE_URL string ("postgres://user:pass@host/db") into Django's DATABASES dict — hosts hand you a URL, Django wants a dict
from decouple import config  # reads .env / real env vars with type casting and defaults; keeps secrets OUT of the repo (this file is committed, .env never is)

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Core secrets & environment ──────────────────────────────────────────────

SECRET_KEY = config(  # signs session cookies, password-reset tokens, and CSRF tokens
    "SECRET_KEY",
    default="django-insecure-dev-key-not-for-production-5j5#u15hoi!s)wd+70_85od",  # dev-only fallback so a fresh clone runs with no .env; production MUST override it
)  # IF WRONG IN PRODUCTION: a leaked or shared key lets an attacker forge session cookies and sign in as anyone — it is the single most damaging value in this file. Generate a fresh one per environment and never reuse the dev key.

DEBUG = config("DEBUG", default=True, cast=bool)  # cast=bool is essential: env vars are STRINGS, and the string "False" is truthy in Python — without the cast, DEBUG would be on in production
# IF WRONG IN PRODUCTION: DEBUG=True renders a full traceback on every error —
# source code, local variables, and settings (including SECRET_KEY) shown to any
# visitor who triggers a 500. It also disables ALLOWED_HOSTS checking and leaks
# every SQL query. This is the #1 real-world Django breach.

ALLOWED_HOSTS = config(  # the Host headers Django will answer to
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost",  # sensible dev default
    cast=lambda hosts: [h.strip() for h in hosts.split(",") if h.strip()],  # env vars can't hold lists, so we ship a comma-separated string and split it — the strip() tolerates "a.com, b.com" with spaces
)
# IF WRONG IN PRODUCTION: too narrow → every request 400s ("Invalid HTTP_HOST")
# and the site is simply down. Too wide (["*"]) → HTTP Host-header poisoning:
# an attacker sets Host: evil.com, and Django happily builds password-reset
# links pointing at their server.

CSRF_TRUSTED_ORIGINS = config(  # origins allowed to POST to us; Django 4+ requires the scheme
    "CSRF_TRUSTED_ORIGINS",
    default="",
    cast=lambda origins: [o.strip() for o in origins.split(",") if o.strip()],
)
# IF WRONG IN PRODUCTION: every form submission on the live domain fails with
# "CSRF verification failed — Origin checking failed" once you're behind HTTPS.
# Set it to https://your-app.onrender.com (scheme included, no trailing slash).

# ─── Applications ────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',
    'menu',  # categories, menu items, reviews — registered so Django discovers its models (for migrations), templates/ folder (APP_DIRS), management commands, and tests
    'accounts',  # our auth app — must be registered so Django finds its templates/ folder (APP_DIRS) and its tests
    'cart',  # session-based cart — no models, but registration is still required so APP_DIRS finds cart/templates/ and the test runner discovers cart/tests.py
    'orders',  # checkout + order history — registered so migrations see its models, APP_DIRS its templates, and the admin its OrderAdmin
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # applies the SECURE_* settings at the bottom of this file; must stay first so it can redirect to HTTPS before anything else runs
    'whitenoise.middleware.WhiteNoiseMiddleware',  # serves /static/ files itself. Position matters: immediately after SecurityMiddleware and BEFORE everything else, so a static file is returned without paying for session loading, auth, or CSRF on every image and stylesheet
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'slappersnsizzlers_v1.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Project-level templates folder (base.html lives here)
        'DIRS': [BASE_DIR / 'slappersnsizzlers_v1' / 'templates'],
        # Also picks up templates inside each app's templates/ folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_count',  # our own: injects {{ cart_count }} into EVERY render so base.html's navbar badge works on all pages — exactly how the two lines above already give every template {{ user }} and {{ messages }}
            ],
        },
    },
]

WSGI_APPLICATION = 'slappersnsizzlers_v1.wsgi.application'  # the entry point gunicorn imports in production; runserver uses it too, so what you test locally is what runs live

# ─── Database ────────────────────────────────────────────────────────────────

DATABASES = {
    'default': dj_database_url.config(  # reads the DATABASE_URL env var
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",  # no DATABASE_URL (i.e. local dev) → fall back to the SQLite file we've used all along, so nothing changes for local work
        conn_max_age=600,  # keep each connection alive 10 minutes instead of opening a new one per request — Postgres connections are expensive to establish, and free tiers cap how many you may hold
        conn_health_checks=True,  # ping a pooled connection before reusing it; without this a connection dropped by the host (idle timeouts are common on free tiers) surfaces as a random 500 on the next request
    )
}
# IF WRONG IN PRODUCTION: pointing at SQLite on Render means the database is a
# file on an EPHEMERAL disk — every deploy resets it to empty. Orders, accounts
# and reviews would silently vanish. Postgres is a separate, persistent service,
# which is why DATABASE_URL must be set there.

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Johannesburg'  # order timestamps display in SAST; USE_TZ below means they're STORED in UTC and converted on render — the correct pairing
USE_I18N = True
USE_TZ = True

# ─── Static files (CSS, JS, images that ship with the code) ──────────────────

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'slappersnsizzlers_v1' / 'static',  # where WE author styles.css
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  # where collectstatic COPIES everything (our files + the admin's) for serving; build.sh runs collectstatic on every deploy

# Why Django doesn't serve static files in production: runserver's static
# handler is a development convenience — single-threaded, no caching, no
# compression, and it re-checks the filesystem on every request. Django's job
# is generating dynamic responses; handing out unchanging bytes is a web
# server's job. In production Django refuses to do it at all (the handler is
# disabled when DEBUG=False), which is why a "working" site suddenly renders
# unstyled the first time you flip DEBUG off — the classic Django deploy shock.
#
# WhiteNoise is the fix that needs no separate nginx/CDN: it serves STATIC_ROOT
# from inside the WSGI app, with compression and far-future cache headers.
STORAGES = {
    "default": {  # uploaded media (see the honest warning below)
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",  # "Compressed" = also writes .gz/.br versions; "Manifest" = renames each file with a hash of its contents (styles.a3f9c1.css) and rewrites references, so caches can be told "keep forever" while a redeploy still busts them instantly
    },
}
# IF WRONG IN PRODUCTION: with ManifestStaticFilesStorage, any {% static %}
# reference to a file that doesn't exist raises ValueError at RENDER time — a
# hard 500, not a silent broken image. That is deliberate (it catches typos at
# deploy), but it means collectstatic must run on every deploy, before traffic.

# ─── Media files (images uploaded through the admin) ─────────────────────────

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# HONEST WARNING — READ BEFORE UPLOADING ANY FOOD PHOTOS ON RENDER:
# Render's free tier gives each deploy a fresh, EPHEMERAL filesystem. Anything
# written to MEDIA_ROOT at runtime — every image the stall uploads through the
# admin — is DELETED on the next deploy, and also whenever the free instance
# spins down after inactivity. The MenuItem rows survive (they're in Postgres),
# but image.url will point at files that no longer exist: broken images, not
# errors, which makes it easy to miss.
#
# THE FIX (not implemented here — out of scope for this module): move media to
# object storage that lives outside the container. Either
#   • Cloudinary — add `cloudinary` + `django-cloudinary-storage`, set the
#     "default" STORAGES backend to Cloudinary's, done; free tier is generous, or
#   • Amazon S3 — add `django-storages[boto3]`, point "default" at
#     S3Boto3Storage with a bucket + IAM credentials in env vars.
# Both work by swapping the "default" entry in STORAGES above; NO model or
# template code changes, because ImageField only ever stores a path and asks the
# storage backend for the URL. That indirection is the whole point of the
# storages API.

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Auth redirects ──────────────────────────────────────────────────────────

LOGIN_URL = '/accounts/login/'  # where @login_required sends anonymous visitors — Django appends ?next=<the page they wanted> so our login view can bounce them back after they sign in
LOGIN_REDIRECT_URL = '/'  # default post-login destination for Django's BUILT-IN LoginView; our function-based login_view redirects explicitly, but setting this keeps behaviour consistent if built-in views are ever used
LOGOUT_REDIRECT_URL = '/'  # same idea for the built-in LogoutView — our logout_view redirects to 'home.index' itself, which resolves to this same path

# ─── PRODUCTION HARDENING (only when DEBUG=False) ────────────────────────────
# Gated on `not DEBUG` so local development over plain http:// still works: every
# setting below assumes HTTPS, and switching them on locally would lock you out
# of your own dev server (endless redirects to an https:// localhost that has no
# certificate). Flipping DEBUG=False in .env is how you test them.

if not DEBUG:
    SECURE_SSL_REDIRECT = True  # 301 any http:// request to https://
    # IF WRONG: users can reach the site over plain HTTP, where session cookies
    # and passwords travel in cleartext for anyone on the same wifi to read.

    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # Render terminates TLS at its load balancer and forwards plain HTTP internally, so Django sees an "insecure" request and — with SSL_REDIRECT on — would redirect forever. This header is how the proxy tells Django "the ORIGINAL request was HTTPS". Only ever set this behind a proxy you trust: a client could otherwise just send the header itself.

    SESSION_COOKIE_SECURE = True  # browsers withhold the session cookie on plain-HTTP requests
    # IF WRONG: the sessionid — which IS the login — can be sniffed on an open
    # network and replayed to impersonate the user (session hijacking).

    CSRF_COOKIE_SECURE = True  # same protection for the CSRF token cookie
    # IF WRONG: a sniffed CSRF token lets an attacker craft form posts that pass
    # our CSRF check, undoing the protection every {% csrf_token %} provides.

    SECURE_HSTS_SECONDS = 31536000  # one year: tells the browser "never speak plain HTTP to this domain again", which closes the gap where the very first http:// request is still interceptable before the redirect
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # extend that promise to every subdomain
    SECURE_HSTS_PRELOAD = True  # allows submission to browsers' built-in preload list, protecting even a first-ever visit
    # ⚠ HSTS IS A ONE-WAY DOOR: browsers CACHE this for the full year and there
    # is no way to reach visitors who already have it. If HTTPS on your domain
    # later breaks, the site is unreachable for them — not "insecure", gone.
    # Start with a small value (e.g. 3600) on a real domain, confirm HTTPS is
    # solid, then raise it. A year is safe here only because *.onrender.com is
    # HTTPS-only and already preloaded by Render.

    SESSION_COOKIE_HTTPONLY = True  # JavaScript can't read document.cookie for the session — limits what an XSS bug can steal (this one is Django's default; stated explicitly so it can't be silently lost)
    SECURE_CONTENT_TYPE_NOSNIFF = True  # sends X-Content-Type-Options: nosniff so a browser won't "helpfully" execute an uploaded .jpg it decides looks like JavaScript
    X_FRAME_OPTIONS = "DENY"  # refuse to be embedded in any <iframe> — blocks clickjacking, where our checkout button is layered invisibly over someone else's page
