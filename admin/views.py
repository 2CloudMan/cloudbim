# -*- coding:utf-8 -*-
import logging
import threading
import json

from django.contrib.auth.models import User, Group

from utils.lib.django_util import render
from utils.lib.exceptions_renderable import PopupException
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import redirect

from utils.conf import LDAP
from utils.hadoop.fs.exceptions import WebHdfsException
from models import UserProfile
from models import get_profile, get_default_user_group
from forms import  GroupEditForm, SuperUserChangeForm, UserChangeForm

# Create your views here.

LOG = logging.getLogger(__name__)

__users_lock = threading.Lock()
__groups_lock = threading.Lock()

def list_users(request):
  is_ldap_setup = bool(LDAP.LDAP_SERVERS.get()) or LDAP.LDAP_URL.get() is not None
  return render("list_users.mako", request, {
      'users': User.objects.all(),
      'users_json': json.dumps(list(User.objects.values_list('id', flat=True))),
      'request': request,
      'is_ldap_setup': is_ldap_setup
  })
  

def list_groups(request):
  is_ldap_setup = bool(LDAP.LDAP_SERVERS.get()) or LDAP.LDAP_URL.get() is not None
  return render("list_groups.mako", request, {
      'groups': Group.objects.all(),
      'groups_json': json.dumps(list(Group.objects.values_list('name', flat=True))),
      'is_ldap_setup': is_ldap_setup
  })


def delete_user(request):
  if not request.user.is_superuser:
    raise PopupException(_("You must be a superuser to delete users."), error_code=401)

  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  ids = request.POST.getlist('user_ids')
  global __users_lock
  __users_lock.acquire()
  try:
    if str(request.user.id) in ids:
      raise PopupException(_("You cannot remove yourself."), error_code=401)

    UserProfile.objects.filter(user__id__in=ids).delete()
    User.objects.filter(id__in=ids).delete()
  finally:
    __users_lock.release()

  request.info(_('The users were deleted.'))
  return redirect(reverse(list_users))


def delete_group(request):
  if not request.user.is_superuser:
    raise PopupException(_("You must be a superuser to delete groups."), error_code=401)

  if request.method == 'POST':
    try:
      group_names = request.POST.getlist('group_names')
      # Get the default group before getting the group, because we may be
      # trying to delete the default group, and it may not have been created yet.
      default_group = get_default_user_group()
      if default_group is not None and default_group.name in group_names:
        raise PopupException(_("The default user group may not be deleted."), error_code=401)
      Group.objects.filter(name__in=group_names).delete()

      request.info(_('The groups were deleted.'))
      return redirect(reverse(list_groups))
    except Group.DoesNotExist:
      raise PopupException(_("Group not found."), error_code=404)
  else:
    return render("delete_group.mako", request, {'path': request.path})


def edit_user(request, username=None):
  """
  edit_user(request, username = None) -> reply

  @type request:        HttpRequest
  @param request:       The request object
  @type username:       string
  @param username:      Default to None, when creating a new user
  """
  if request.user.username != username and not request.user.is_superuser:
    raise PopupException(_("You must be a superuser to add or edit another user."), error_code=401)

  if username is not None:
    instance = User.objects.get(username=username)
  else:
    instance = None

  if request.user.is_superuser:
    form_class = SuperUserChangeForm
  else:
    form_class = UserChangeForm

  if request.method == 'POST':
    form = form_class(request.POST, instance=instance)
    if request.user.is_superuser and request.user.username != username:
      form.fields.pop("password_old")
    if form.is_valid(): # All validation rules pass
      if instance is None:
        instance = form.save()
        get_profile(instance)
      else:
        if username != form.instance.username:
          raise PopupException(_("You cannot change a username."), error_code=401)
        if request.user.username == username and not form.instance.is_active:
          raise PopupException(_("You cannot make yourself inactive."), error_code=401)

        global __users_lock
        __users_lock.acquire()
        try:
          # form.instance (and instance) now carry the new data
          orig = User.objects.get(username=username)
          if orig.is_superuser:
            if not form.instance.is_superuser or not form.instance.is_active:
              _check_remove_last_super(orig)
          else:
            if form.instance.is_superuser and not request.user.is_superuser:
              raise PopupException(_("You cannot make yourself a superuser."), error_code=401)

          # All ok
          form.save()
          request.info(_('User information updated'))
        finally:
          __users_lock.release()

      # Ensure home directory is created, if necessary.
      if form.cleaned_data['ensure_home_directory']:
        try:
          ensure_home_directory(request.fs, instance.username)
        except (IOError, WebHdfsException), e:
          request.error(_('Cannot make home directory for user %s.' % instance.username))
      if request.user.is_superuser:
        return redirect(reverse(list_users))
      else:
        return redirect(reverse(edit_user, kwargs={'username': username}))
  else:
    default_user_group = get_default_user_group()
    initial = {
      'ensure_home_directory': instance is None,
      'groups': default_user_group and [default_user_group] or []
    }
    form = form_class(instance=instance, initial=initial)
    if request.user.is_superuser and request.user.username != username:
      form.fields.pop("password_old")

  return render('edit_user.mako', request, dict(form=form, username=username))


def edit_group(request, name=None):
  """
  edit_group(request, name = None) -> reply

  @type request:        HttpRequest
  @param request:       The request object
  @type name:       string
  @param name:      Default to None, when creating a new group

  Only superusers may create a group
  """
  if not request.user.is_superuser:
    raise PopupException(_("You must be a superuser to add or edit a group."), error_code=401)

  if name is not None:
    instance = Group.objects.get(name=name)
  else:
    instance = None

  if request.method == 'POST':
    form = GroupEditForm(request.POST, instance=instance)
    if form.is_valid():
      form.save()
      request.info(_('Group information updated'))
      return list_groups(request)

  else:
    form = GroupEditForm(instance=instance)

  return render('edit_group.mako', request, dict(form=form, action=request.path, name=name))


def ensure_home_directory(fs, username):
  """
  Adds a users home directory if it doesn't already exist.

  Throws IOError, WebHdfsException.
  """
  home_dir = '/user/%s' % username
  fs.do_as_user(username, fs.create_home_dir, home_dir)
  

def ensure_project_directory(fs, proj_slug):
    proj_dir = '/project/%s' % proj_slug
    
    # 暂时使用超级管理员
    fs.do_as_superuser(fs.create_home_dir, proj_dir)

def _check_remove_last_super(user_obj):
  """Raise an error if we're removing the last superuser"""
  if not user_obj.is_superuser:
    return

  # Is there any other active superuser left?
  all_active_su = User.objects.filter(is_superuser__exact = True,
                                      is_active__exact = True)
  num_active_su = all_active_su.count()
  assert num_active_su >= 1, _("No active superuser configured.")
  if num_active_su == 1:
    raise PopupException(_("You cannot remove the last active superuser from the configuration."), error_code=401)


def get_file_permission(request):
    pass


def add_file_permission(request):
    pass


def edit_file_permission(request, app=None, priv=None):
  """
  edit_permission(request, app = None, priv = None) -> reply

  @type request:        HttpRequest
  @param request:       The request object
  @type app:       string
  @param app:      Default to None, specifies the app of the privilege
  @type priv:      string
  @param priv      Default to None, the action of the privilege

  Only superusers may modify permissions
  """
  pass