from django.shortcuts import render

# Create your views here.

def ensure_home_directory(fs, username):
  """
  Adds a users home directory if it doesn't already exist.

  Throws IOError, WebHdfsException.
  """
  home_dir = '/user/%s' % username
  fs.do_as_user(username, fs.create_home_dir, home_dir)