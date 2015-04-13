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

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'admin',
    'auth',
    'hbase',
    'hdfs',
    'main',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'djangomako.middleware.MakoMiddleware',
    'utils.middleware.ClusterMiddleware',
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

# templates config, define how to import templates.
TEMPLATE_LOADERS = (
                    'django.template.loader.filesystem.Loader',
                    'django.template.loader.app_directories.Loader',
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

MAKO_TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'hdfs/templates').replace('\\', '/'),
    os.path.join(BASE_DIR, 'templates').replace('\\', '/'),
)

# initial conf
from utils.lib.paths import get_desktop_root
_config_dir = os.getenv("CLOUDBIM_CONF_DIR", get_desktop_root("conf"))
_desktop_conf_modules = [dict(module=utils.conf, config_key=None)]
conf.initialize(_desktop_conf_modules, _config_dir)

import utils.hadoop.conf
import hdfs.conf
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
#                      {"module": hbase.conf,
#                       "config_key": None}
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
