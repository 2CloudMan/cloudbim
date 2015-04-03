from django.contrib.staticfiles.storage import staticfiles_storage

from django.conf import  settings


def static(path):
  """
  Returns the URL to a file using the staticfiles's storage engine
  """
  try:
    return staticfiles_storage.url(path)
  except ValueError:
    # django.contrib.staticfiles raises a ValueError if the file we are looking
    # for is not in the staticfiles directory. This will result in a 500 error
    # in a mako script, which is a little unfriendly. Instead we'll return a
    # path to a non-existing file so the template renders and we can see the
    # missing file in the logs.
    return settings.STATIC_URL + path