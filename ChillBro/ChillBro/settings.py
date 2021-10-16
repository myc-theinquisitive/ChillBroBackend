"""
Django settings for ChillBro project.
Generated by 'django-admin startproject' using Django 2.2.8.
For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'd3rgelo^8wck52w2^g&1vlei$a$&s23g0fa&z0=2ic-mshux%d'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'UserApp',
    'Coupons',
    'Entity',
    'authentication',
    'Issues',
    'Address',
    'Bookings',
    'Product',
    'taggit',
    'kvstore',
    'Payments',
    'ReviewsRatings',
    'Refer',
    'Cart',
    'WishList',
    'Wallet',
    'Notifications',
    'HelpCenter',
    'channels',
    'EmployeeManagement',
    'JobPortal',
    'thumbnails',
]


FCM_DJANGO_SETTINGS = {
        "FCM_SERVER_KEY": "AIzaSyBkAqi63WPerzKQ9-TSrA8pEAH6yTXLrfs"
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ChillBro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ChillBro.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

IS_SERVER = False

if IS_SERVER:
    DEBUG = True

    FILE_UPLOAD_PERMISSIONS = 0o644
    # STATIC_URL = 'https://chillbro.co.in/'
    # STATIC_ROOT = 'chillbro_backend/'
    MEDIA_URL = 'https://chillbro.co.in/chillbro_backend/'
    MEDIA_ROOT = '/home/ffs2imp1oh0k/public_html/chillbro_backend/'
    DEFAULT_FILE_STORAGE = '/home/ffs2imp1oh0k/public_html/chillbro_backend/'

    ALLOWED_HOSTS = ["chillbro.co.in", "184.168.127.251"]

    #MY EMAIL SETTING

    EMAIL_FROM = 'no-reply@chillbro.co.in'
    EMAIL_BCC = 'team.theinquisitive@gmail.com' # Any mail for BCC can be given

    EMAIL_BACKEND ='django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtpout.secureserver.net'  #Hosted on namecheap Ex: mail.pure.com
    EMAIL_USE_TLS = False
    EMAIL_PORT = 80 #This will be different based on your Host, for Namecheap I use this`
    EMAIL_USE_SSL = False
    EMAIL_HOST_USER = 'no-reply@chillbro.co.in' # Ex: info@pure.com
    EMAIL_HOST_PASSWORD = 'MissionImpossible@2020' # for the email you created through cPanel. The password for that
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


    LOG_PATH = "/home/ffs2imp1oh0k/adminpanel_logs/"
    LOGGING = {
        'version': 1,
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            }
        },
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s]- %(message)s'}

        },
        'handlers': {
            'django_error': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOG_PATH + 'django.log',
                'formatter': 'standard'
            },
            'info': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOG_PATH + 'info.log',
                'formatter': 'standard'
            },
            'console': {
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
            }
        },
        'loggers': {
            'info': {
                'handlers': ['info', "console"],
                'level': 'DEBUG',
                'propagate': True
            },
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True,
            },
            'django.request': {
                'handlers': ['django_error', 'console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['console'],
            }
        }
    }

else:
    DEBUG = True

    MEDIA_URL = 'http://127.0.0.1:8000/'
    MEDIA_ROOT = ''
    STATIC_ROOT = 'static/'

    ALLOWED_HOSTS = []

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    # EMAIL_PORT = os.environ.get('AUTHEMAIL_EMAIL_PORT') or 587
    EMAIL_PORT = 587
    EMAIL_HOST_USER = ' myc.theinquisitive@gmail.com'
    EMAIL_HOST_PASSWORD = 'MissionMyc'
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False


    LOGGING = {
        'version': 1,
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['console'],
            },
            'celery': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        }
    }


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'ChillBro.authentication.JWTAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
    ),
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    # 'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables.filters.DatatablesFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'PAGE_SIZE': 10,
}

AUTH_USER_MODEL = 'UserApp.MyUser'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# Constants
DSC_COUPON_CODE_LENGTH = 15
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
IMAGE_REPLACED_STRING = "home/ffs2imp1oh0k/public_html/chillbro_backend/"


TAGGIT_CASE_INSENSITIVE = True
MYC_ID = "MYC"

BROKER_URL = 'redis://184.168.127.251:6379/'
CELERY_RESULT_BACKEND = 'redis://184.168.127.251:6379/'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = "Asia/Kolkata"
CELERY_IMPORTS = ('authentication.tasks', 'Bookings.tasks',)

RAZORPAY_API_KEY = "rzp_test_Ggvw8pTdJ3SnAg"
RAZORPAY_API_SECRET = "HQrPh4O1A1bIYP2To2yMjqMJ"

CHANNEL_LAYERS = {
    'default': {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
        # 'CONFIG': {
        #     "hosts": [("127.0.0.1", 6379)],
        # },
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://184.168.127.251:6379/',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

ASGI_APPLICATION = 'ChillBro.routing.application'

THUMBNAILS = {
    'METADATA': {
        'BACKEND': 'thumbnails.backends.metadata.DatabaseBackend',
    },
    'STORAGE': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'SIZES': {
        'small': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 10, 'height': 10},
                {'PATH': 'thumbnails.processors.crop', 'width': 80, 'height': 80}
            ],
            'POST_PROCESSORS': [
                {
                    'PATH': 'thumbnails.post_processors.optimize',
                    'png_command': 'optipng -force -o7 "%(filename)s"',
                    'jpg_command': 'jpegoptim -f --strip-all "%(filename)s"',
                },
            ],
        },
        'large': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 20, 'height': 20},
                {'PATH': 'thumbnails.processors.flip', 'direction': 'horizontal'}
            ],
        }
    }
}
