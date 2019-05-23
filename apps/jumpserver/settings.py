"""
Django settings for jumpserver project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import sys

import ldap
from django.urls import reverse_lazy

from . import const
from .conf import load_user_config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_DIR)

CONFIG = load_user_config()
LOG_DIR = os.path.join(PROJECT_DIR, 'logs')
JUMPSERVER_LOG_FILE = os.path.join(LOG_DIR, 'jumpserver.log')
ANSIBLE_LOG_FILE = os.path.join(LOG_DIR, 'ansible.log')
GUNICORN_LOG_FILE = os.path.join(LOG_DIR, 'gunicorn.log')
VERSION = const.VERSION

if not os.path.isdir(LOG_DIR):
    os.makedirs(LOG_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONFIG.SECRET_KEY

# SECURITY WARNING: keep the token secret, remove it if all coco, guacamole ok
BOOTSTRAP_TOKEN = CONFIG.BOOTSTRAP_TOKEN

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = CONFIG.DEBUG

# Absolute url for some case, for example email link
SITE_URL = CONFIG.SITE_URL

# LOG LEVEL
LOG_LEVEL = CONFIG.LOG_LEVEL

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'orgs.apps.OrgsConfig',
    'users.apps.UsersConfig',
    'assets.apps.AssetsConfig',
    'perms.apps.PermsConfig',
    'ops.apps.OpsConfig',
    'settings.apps.SettingsConfig',
    'common.apps.CommonConfig',
    'terminal.apps.TerminalConfig',
    'audits.apps.AuditsConfig',
    'authentication.apps.AuthenticationConfig',  # authentication
    'rest_framework',
    'rest_framework_swagger',
    'drf_yasg',
    'django_filters',
    'bootstrap3',
    'captcha',
    'django_celery_beat',
    'django_celery_results',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]


XPACK_DIR = os.path.join(BASE_DIR, 'xpack')
XPACK_ENABLED = os.path.isdir(XPACK_DIR)
XPACK_TEMPLATES_DIR = []
XPACK_CONTEXT_PROCESSOR = []

if XPACK_ENABLED:
    from xpack.utils import get_xpack_templates_dir, get_xpack_context_processor
    INSTALLED_APPS.append('xpack.apps.XpackConfig')
    XPACK_TEMPLATES_DIR = get_xpack_templates_dir(BASE_DIR)
    XPACK_CONTEXT_PROCESSOR = get_xpack_context_processor()

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'authentication.backends.openid.middleware.OpenIDAuthenticationMiddleware',
    'jumpserver.middleware.TimezoneMiddleware',
    'jumpserver.middleware.DemoMiddleware',
    'jumpserver.middleware.RequestMiddleware',
    'orgs.middleware.OrgMiddleware',
]

ROOT_URLCONF = 'jumpserver.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), *XPACK_TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'jumpserver.context_processor.jumpserver_processor',
                'orgs.context_processor.org_processor',
                *XPACK_CONTEXT_PROCESSOR,
            ],
        },
    },
]

# WSGI_APPLICATION = 'jumpserver.wsgi.applications'

LOGIN_REDIRECT_URL = reverse_lazy('index')
LOGIN_URL = reverse_lazy('authentication:login')

SESSION_COOKIE_DOMAIN = CONFIG.SESSION_COOKIE_DOMAIN
CSRF_COOKIE_DOMAIN = CONFIG.CSRF_COOKIE_DOMAIN
SESSION_COOKIE_AGE = CONFIG.SESSION_COOKIE_AGE
SESSION_EXPIRE_AT_BROWSER_CLOSE = CONFIG.SESSION_EXPIRE_AT_BROWSER_CLOSE
SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS = {
    'host': CONFIG.REDIS_HOST,
    'port': CONFIG.REDIS_PORT,
    'password': CONFIG.REDIS_PASSWORD,
    'db': CONFIG.REDIS_DB_SESSION,
    'prefix': 'auth_session',
    'socket_timeout': 1,
    'retry_on_timeout': False
}

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DB_OPTIONS = {}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.{}'.format(CONFIG.DB_ENGINE.lower()),
        'NAME': CONFIG.DB_NAME,
        'HOST': CONFIG.DB_HOST,
        'PORT': CONFIG.DB_PORT,
        'USER': CONFIG.DB_USER,
        'PASSWORD': CONFIG.DB_PASSWORD,
        'ATOMIC_REQUESTS': True,
        'OPTIONS': DB_OPTIONS
    }
}
DB_CA_PATH = os.path.join(PROJECT_DIR, 'data', 'ca.pem')
if CONFIG.DB_ENGINE.lower() == 'mysql':
    DB_OPTIONS['init_command'] = "SET sql_mode='STRICT_TRANS_TABLES'"
    if os.path.isfile(DB_CA_PATH):
        DB_OPTIONS['ssl'] = {'ca': DB_CA_PATH}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators
#
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Logging setting
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'main': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '%(asctime)s [%(module)s %(levelname)s] %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'msg': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'main'
        },
        'file': {
            'encoding': 'utf8',
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*1024*100,
            'backupCount': 7,
            'formatter': 'main',
            'filename': JUMPSERVER_LOG_FILE,
        },
        'ansible_logs': {
            'encoding': 'utf8',
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'main',
            'maxBytes': 1024*1024*100,
            'backupCount': 7,
            'filename': ANSIBLE_LOG_FILE,
        },
        'gunicorn_file': {
            'encoding': 'utf8',
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'msg',
            'maxBytes': 1024*1024*100,
            'backupCount': 2,
            'filename': GUNICORN_LOG_FILE,
        },
        'gunicorn_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'msg'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': False,
            'level': LOG_LEVEL,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'jumpserver': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
        },
        'jumpserver.users.api': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
        },
        'jumpserver.users.view': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
        },
        'ops.ansible_api': {
            'handlers': ['console', 'ansible_logs'],
            'level': LOG_LEVEL,
        },
        'django_auth_ldap': {
            'handlers': ['console', 'file'],
            'level': "INFO",
        },
        'gunicorn': {
            'handlers': ['gunicorn_console', 'gunicorn_file'],
            'level': 'INFO',
        },
        # 'django.db': {
        #     'handlers': ['console', 'file'],
        #     'level': 'DEBUG'
        # }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/
# LANGUAGE_CODE = 'en'
LANGUAGE_CODE = 'zh'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# I18N translation
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_DIR, "data", "static")
STATIC_DIR = os.path.join(BASE_DIR, "static")

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

# Media files (File, ImageField) will be save these

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(PROJECT_DIR, 'data', 'media').replace('\\', '/') + '/'

# Use django-bootstrap-form to format template, input max width arg
# BOOTSTRAP_COLUMN_COUNT = 11

# Init data or generate fake data source for development
FIXTURE_DIRS = [os.path.join(BASE_DIR, 'fixtures'), ]

# Email config
EMAIL_HOST = 'smtp.jumpserver.org'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'noreply@jumpserver.org'
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_SSL = False
EMAIL_USE_TLS = False
EMAIL_SUBJECT_PREFIX = '[JMS] '

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': (
        'common.permissions.IsOrgAdmin',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',  # debug
        'authentication.backends.api.AccessKeyAuthentication',
        'authentication.backends.api.AccessTokenAuthentication',
        'authentication.backends.api.PrivateTokenAuthentication',
        'authentication.backends.api.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'ORDERING_PARAM': "order",
    'SEARCH_PARAM': "search",
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S %z',
    'DATETIME_INPUT_FORMATS': ['%Y-%m-%d %H:%M:%S %z'],
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    # 不能兼容DRF的分页设置，资产树变UNDEFINED
    # 'DEFAULT_PAGINATION_CLASS': 'REST_FRAMEWORK.PAGINATION.PAGENUMBERPAGINATION',
    # 'PAGE_SIZE': 5,
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Custom User Auth model
AUTH_USER_MODEL = 'users.User'

# File Upload Permissions
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# OTP settings
OTP_ISSUER_NAME = CONFIG.OTP_ISSUER_NAME
OTP_VALID_WINDOW = CONFIG.OTP_VALID_WINDOW

# Auth LDAP settings
AUTH_LDAP = False
AUTH_LDAP_SERVER_URI = 'ldap://localhost:389'
AUTH_LDAP_BIND_DN = 'cn=admin,dc=jumpserver,dc=org'
AUTH_LDAP_BIND_PASSWORD = ''
AUTH_LDAP_SEARCH_OU = 'ou=tech,dc=jumpserver,dc=org'
AUTH_LDAP_SEARCH_FILTER = '(cn=%(user)s)'
AUTH_LDAP_START_TLS = False
AUTH_LDAP_USER_ATTR_MAP = {"username": "cn", "name": "sn", "email": "mail"}
# AUTH_LDAP_GROUP_SEARCH_OU = CONFIG.AUTH_LDAP_GROUP_SEARCH_OU
# AUTH_LDAP_GROUP_SEARCH_FILTER = CONFIG.AUTH_LDAP_GROUP_SEARCH_FILTER
# AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
#    AUTH_LDAP_GROUP_SEARCH_OU, ldap.SCOPE_SUBTREE, AUTH_LDAP_GROUP_SEARCH_FILTER
# )
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_TIMEOUT: 30
}
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 1
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_BACKEND = 'authentication.backends.ldap.LDAPAuthorizationBackend'

if AUTH_LDAP:
    AUTHENTICATION_BACKENDS.insert(0, AUTH_LDAP_BACKEND)

# openid
# Auth OpenID settings
BASE_SITE_URL = CONFIG.BASE_SITE_URL
AUTH_OPENID = CONFIG.AUTH_OPENID
AUTH_OPENID_SERVER_URL = CONFIG.AUTH_OPENID_SERVER_URL
AUTH_OPENID_REALM_NAME = CONFIG.AUTH_OPENID_REALM_NAME
AUTH_OPENID_CLIENT_ID = CONFIG.AUTH_OPENID_CLIENT_ID
AUTH_OPENID_CLIENT_SECRET = CONFIG.AUTH_OPENID_CLIENT_SECRET
AUTH_OPENID_BACKENDS = [
    'authentication.backends.openid.backends.OpenIDAuthorizationPasswordBackend',
    'authentication.backends.openid.backends.OpenIDAuthorizationCodeBackend',
]

if AUTH_OPENID:
    LOGIN_URL = reverse_lazy("authentication:openid:openid-login")
    LOGIN_COMPLETE_URL = reverse_lazy("authentication:openid:openid-login-complete")
    AUTHENTICATION_BACKENDS.insert(0, AUTH_OPENID_BACKENDS[0])
    AUTHENTICATION_BACKENDS.insert(0, AUTH_OPENID_BACKENDS[1])

# Radius Auth
AUTH_RADIUS = CONFIG.AUTH_RADIUS
AUTH_RADIUS_BACKEND = 'authentication.backends.radius.RadiusBackend'
RADIUS_SERVER = CONFIG.RADIUS_SERVER
RADIUS_PORT = CONFIG.RADIUS_PORT
RADIUS_SECRET = CONFIG.RADIUS_SECRET

if AUTH_RADIUS:
    AUTHENTICATION_BACKENDS.insert(0, AUTH_RADIUS_BACKEND)

# Dump all celery log to here
CELERY_LOG_DIR = os.path.join(PROJECT_DIR, 'data', 'celery')

# Celery using redis as broker
CELERY_BROKER_URL = 'redis://:%(password)s@%(host)s:%(port)s/%(db)s' % {
    'password': CONFIG.REDIS_PASSWORD,
    'host': CONFIG.REDIS_HOST,
    'port': CONFIG.REDIS_PORT,
    'db': CONFIG.REDIS_DB_CELERY,
}
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_RESULT_BACKEND = 'django-db' # CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_ACCEPT_CONTENT = ['json', 'pickle']
CELERY_RESULT_EXPIRES = 3600
# CELERY_WORKER_LOG_FORMAT = '%(asctime)s [%(module)s %(levelname)s] %(message)s'
# CELERY_WORKER_LOG_FORMAT = '%(message)s'
# CELERY_WORKER_TASK_LOG_FORMAT = '%(task_id)s %(task_name)s %(message)s'
CELERY_WORKER_TASK_LOG_FORMAT = '%(message)s'
# CELERY_WORKER_LOG_FORMAT = '%(asctime)s [%(module)s %(levelname)s] %(message)s'
CELERY_WORKER_LOG_FORMAT = '%(message)s'
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_WORKER_REDIRECT_STDOUTS = True
CELERY_WORKER_REDIRECT_STDOUTS_LEVEL = "INFO"
# CELERY_WORKER_HIJACK_ROOT_LOGGER = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = 40
CELERY_TASK_SOFT_TIME_LIMIT = 3600

# Cache use redis
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'redis://:%(password)s@%(host)s:%(port)s/%(db)s' % {
            'password': CONFIG.REDIS_PASSWORD,
            'host': CONFIG.REDIS_HOST,
            'port': CONFIG.REDIS_PORT,
            'db': CONFIG.REDIS_DB_CACHE,
        }
    }
}

# Captcha settings, more see https://django-simple-captcha.readthedocs.io/en/latest/advanced.html
CAPTCHA_IMAGE_SIZE = (80, 33)
CAPTCHA_FOREGROUND_COLOR = '#001100'
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)
CAPTCHA_TEST_MODE = CONFIG.CAPTCHA_TEST_MODE

COMMAND_STORAGE = {
    'ENGINE': 'terminal.backends.command.db',
}

DEFAULT_TERMINAL_COMMAND_STORAGE = {
    "default": {
        "TYPE": "server",
    },
}

TERMINAL_COMMAND_STORAGE = {
    # 'ali-es': {
    #     'TYPE': 'elasticsearch',
    #     'HOSTS': ['http://elastic:changeme@localhost:9200'],
    # },
}

DEFAULT_TERMINAL_REPLAY_STORAGE = {
    "default": {
        "TYPE": "server",
    },
}

TERMINAL_REPLAY_STORAGE = {
}


SECURITY_MFA_AUTH = False
SECURITY_LOGIN_LIMIT_COUNT = 7
SECURITY_LOGIN_LIMIT_TIME = 30  # Unit: minute
SECURITY_MAX_IDLE_TIME = 30  # Unit: minute
SECURITY_PASSWORD_EXPIRATION_TIME = 9999  # Unit: day
SECURITY_PASSWORD_MIN_LENGTH = 6  # Unit: bit
SECURITY_PASSWORD_UPPER_CASE = False
SECURITY_PASSWORD_LOWER_CASE = False
SECURITY_PASSWORD_NUMBER = False
SECURITY_PASSWORD_SPECIAL_CHAR = False
SECURITY_PASSWORD_RULES = [
    'SECURITY_PASSWORD_MIN_LENGTH',
    'SECURITY_PASSWORD_UPPER_CASE',
    'SECURITY_PASSWORD_LOWER_CASE',
    'SECURITY_PASSWORD_NUMBER',
    'SECURITY_PASSWORD_SPECIAL_CHAR'
]

TERMINAL_PASSWORD_AUTH = CONFIG.TERMINAL_PASSWORD_AUTH
TERMINAL_PUBLIC_KEY_AUTH = CONFIG.TERMINAL_PUBLIC_KEY_AUTH
TERMINAL_HEARTBEAT_INTERVAL = CONFIG.TERMINAL_HEARTBEAT_INTERVAL
TERMINAL_ASSET_LIST_SORT_BY = CONFIG.TERMINAL_ASSET_LIST_SORT_BY
TERMINAL_ASSET_LIST_PAGE_SIZE = CONFIG.TERMINAL_ASSET_LIST_PAGE_SIZE
TERMINAL_SESSION_KEEP_DURATION = CONFIG.TERMINAL_SESSION_KEEP_DURATION
TERMINAL_HOST_KEY = CONFIG.TERMINAL_HOST_KEY
TERMINAL_HEADER_TITLE = CONFIG.TERMINAL_HEADER_TITLE
TERMINAL_TELNET_REGEX = CONFIG.TERMINAL_TELNET_REGEX

# Django bootstrap3 setting, more see http://django-bootstrap3.readthedocs.io/en/latest/settings.html
BOOTSTRAP3 = {
    'horizontal_label_class': 'col-md-2',
    # Field class to use in horizontal forms
    'horizontal_field_class': 'col-md-9',
    # Set placeholder attributes to label if no placeholder is provided
    'set_placeholder': False,
    'success_css_class': '',
    'required_css_class': 'required',
}

TOKEN_EXPIRATION = CONFIG.TOKEN_EXPIRATION
DISPLAY_PER_PAGE = CONFIG.DISPLAY_PER_PAGE
DEFAULT_EXPIRED_YEARS = 70
USER_GUIDE_URL = ""


SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'jumpserver.swagger.CustomSwaggerAutoSchema',
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
}

# Default email suffix
EMAIL_SUFFIX = CONFIG.EMAIL_SUFFIX
LOGIN_LOG_KEEP_DAYS = CONFIG.LOGIN_LOG_KEEP_DAYS

# User or user group permission cache time, default 3600 seconds
ASSETS_PERM_CACHE_TIME = CONFIG.ASSETS_PERM_CACHE_TIME

# Asset user auth external backend, default AuthBook backend
BACKEND_ASSET_USER_AUTH_VAULT = False
