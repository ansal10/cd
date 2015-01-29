"""
Django settings for coupondunia project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
DEFAULT_SECRET_KEY = '3iy-!-d$!pc_ll$#$elg&cpr@*tfn-d5&n9ag=)%#()t$$5%5^'
SECRET_KEY = os.environ.get('SECRET_KEY', DEFAULT_SECRET_KEY)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cricket',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'coupondunia.urls'

WSGI_APPLICATION = 'coupondunia.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'


# Parse database configuration from $DATABASE_URL
# DATABASES['default'] =  dj_database_url.config()

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'
LOGIN_URL = '/login'


STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# #---------------------------------- Local Connection To Database START---------------------------------------#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',     # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#         'NAME': 'cd',                                           # Or path to database file if using sqlite3.
#         'USER': 'postgres',                                          # Not used with sqlite3.
#         'PASSWORD': 'ansal10',                                      # Not used with sqlite3.
#         'HOST': 'localhost',                                    # Set to empty string for localhost. Not used with sqlite3.
#         'PORT': '5432',
#     }
# }
# #---------------------------------- Local Connection To Database END---------------------------------------#


# #---------------------------------- heroku Connection To Database START---------------------------------------#



DATABASES['default']=dj_database_url.config()



# #---------------------------------- heroku Connection To Database END---------------------------------------#


ALLOWED_TEAM_COMBINATION = [
         {'BATSMEN':3,'WKEEPER':1 , 'ALLROUND':2, 'BOWLER':2},
         {'BATSMEN':3,'WKEEPER':1 , 'ALLROUND':1, 'BOWLER':3},
         {'BATSMEN':4,'WKEEPER':1 , 'ALLROUND':1, 'BOWLER':2}
    ]

NUMBER_OF_PLAYERS_ALLOWED_IN_TEAM = 8

MAX_AMOUNT_ALLOTED_TO_TEAM = 100.0