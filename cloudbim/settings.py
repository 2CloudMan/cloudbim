# -*- coding: utf-8 -*-
"""
Django settings for cloudbim project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf.global_settings import TEMPLATE_LOADERS
import utils.conf
from utils.lib import conf

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'n2)44vc16h#eb69!3&6-f=h@c9kt@nfd$2ofcwp8rj!efel)42'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'south',

    'admin',
    'auth',
    'main',
    'hbase',
    'hdfs',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.transaction.TransactionMiddleware',

    
    'utils.middleware.AjaxMiddleware',
    'utils.middleware.ExceptionMiddleware',
    'utils.middleware.ClusterMiddleware',
    'utils.middleware.GroupMiddleware',
    'djangomako.middleware.MakoMiddleware',
)

ROOT_URLCONF = 'cloudbim.urls'

WSGI_APPLICATION = 'cloudbim.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cloudbim',
        'USER': 'root',
        'PASSWORD': '123456',
        'PORT': 3306,
        'HOST': '127.0.0.1',
    }
}

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


HADOOP_PROJECT_DIR='/cloudbim/'

DOWNLOAD_CHUNK_SIZE = 64 * 1024 * 1024 # 64MB

# templates config, define how to import templates.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or 
    # "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'templates').replace('\\', '/'),
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
# STATIC_URL = os.path.join('static/').replace('\\', '/')
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)
# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'static').replace('\\', '/'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'collect_static').replace('\\', '/')

# MAKO_TEMPLATE_DIRS = (
#     os.path.join(BASE_DIR, 'hdfs/templates').replace('\\', '/'),
#     os.path.join(BASE_DIR, 'templates').replace('\\', '/'),
# )

# initial conf
from utils.lib.paths import get_desktop_root
_config_dir = os.getenv("CLOUDBIM_CONF_DIR", get_desktop_root("conf"))
_desktop_conf_modules = [dict(module=utils.conf, config_key=None)]
conf.initialize(_desktop_conf_modules, _config_dir)

import utils.hadoop.conf
import hdfs.conf
import hbase.conf
# import hbase.conf
_lib_conf_modules = [
                   {
                    "module": utils.hadoop.conf,
                    "config_key": None
                    },
                    ]

_app_conf_modules = [
                     {
                      "module": hdfs.conf,
                      "config_key": None
                      },
                    {"module": hbase.conf,
                     "config_key": None
                     },
                     {"module": utils.conf,
                      "config_key": None}
                     ]
conf.initialize(_lib_conf_modules, _config_dir)
conf.initialize(_app_conf_modules, _config_dir)


# cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-cloudbim'
    }
}


# Desktop supports only one authentication backend.
AUTHENTICATION_BACKENDS = (utils.conf.AUTH.BACKEND.get(),)
if utils.conf.DEMO_ENABLED.get():
  AUTHENTICATION_BACKENDS = ('auth.backend.DemoBackend',)


# hbase permission key
HBASE_QUERY_PERM = 'q'
HBASE_INSERT_PERM = 'i'
HBASE_DELETE_PERM = 'd'

NEED_PERMISSION=True

INIT_FILE_PERM_OWN_GRP = 'rw'
INIT_FILE_PERM_PROJ_GRP = 'rw' 
INIT_DIR_PERM_OWN_GRP='rw'
INIT_DIR_PERM_PROJ_GRP = 'rw'

# Keep default values up to date
TEMPLATE_CONTEXT_PROCESSORS = (
  'django.contrib.auth.context_processors.auth',
  'django.core.context_processors.debug',
  'django.core.context_processors.i18n',
  'django.core.context_processors.media',
  'django.core.context_processors.request',
  'django.contrib.messages.context_processors.messages',
   # Not default
   'utils.context_processors.app_name',
)


# Insert our HDFS upload handler
FILE_UPLOAD_HANDLERS = (
  'utils.hadoop.fs.upload.HDFSfileUploadHandler',
  'django.core.files.uploadhandler.MemoryFileUploadHandler',
  'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] '\
                '[%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
    },
    'filters': {
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/', 'all.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
         'error_handler': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/', 'error.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['default', 'error_handler'],
            'propagate': False,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'hdfs': {
            'handlers': ['default', 'error_handler'],
            'propagate': True,
            'level': 'INFO',
        },
        'hbase': {
            'handlers': ['default', 'error_handler'],
            'propagate': True,
            'level': 'INFO',
        },
        'auth': {
            'handlers': ['default', 'error_handler'],
            'propagate': True,
            'level': 'INFO',
        },
        'utils': {
            'handlers': ['default', 'error_handler'],
            'propagate': True,
            'level': 'INFO',
        },
        'main': {
            'handlers': ['default', 'error_handler'],
            'propagate': True,
            'level': 'INFO',
        },
        'admin': {
            'handlers': ['default', 'error_handler'],
            'propagate': True,
            'level': 'INFO',
        },
    }
}
