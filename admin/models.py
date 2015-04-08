from django.db import models
from enum import Enum
import logging

from django.db import connection, models
from django.contrib.auth import models as auth_models
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _t
from django.utils import timezone

from utils.lib.exceptions_renderable import PopupException
from utils.hadoop import cluster

import conf

# Create your models here.
LOG = logging.getLogger(__name__)


class UserProfile(models.Model):
  """
  WARNING: Some of the columns in the UserProfile object have been added
  via south migration scripts. During an upgrade that modifies this model,
  the columns in the django ORM database will not match the
  actual object defined here, until the latest migration has been executed.
  The code that does the actual UserProfile population must reside in the most
  recent migration that modifies the UserProfile model.

  for user in User.objects.all():
    try:
      p = orm.UserProfile.objects.get(user=user)
    except orm.UserProfile.DoesNotExist:
      create_profile_for_user(user)

  IF ADDING A MIGRATION THAT MODIFIES THIS MODEL, MAKE SURE TO MOVE THIS CODE
  OUT OF THE CURRENT MIGRATION, AND INTO THE NEW ONE, OR UPGRADES WILL NOT WORK
  PROPERLY
  """
  # Enum for describing the creation method of a user.
  CreationMethod = Enum('HUE', 'EXTERNAL')

  user = models.ForeignKey(auth_models.User, unique=True)
  home_directory = models.CharField(editable=True, max_length=1024, null=True)
  creation_method = models.CharField(editable=True, null=False, max_length=64, default=CreationMethod.HUE)

  def get_groups(self):
    return self.user.groups.all()


class Project(models.Model):
    name = models.CharField(max_length=80, unique=True)
    project_directory = models.CharField(editable=True, max_length=1024, null=True)
    created_time = models.DateTimeField(default=timezone.now)
    roles = models.ManyToManyField(auth_models.Group)

class GroupPermission(models.Model):
  """
  Represents the permissions a group has.
  """
  group = models.ForeignKey(auth_models.Group)
  bim_permission = models.ForeignKey("BimFilePermission")


# Permission Management
class BimFilePermission(models.Model):
  """
  Set of non-object specific permissions that an app supports.

  For now, we only assign permissions to groups, though that may change.
  """
  file = models.CharField(max_length=30)
  action = models.CharField(max_length=100)
  description = models.CharField(max_length=255)

  groups = models.ManyToManyField(auth_models.Group, through=GroupPermission)

  def __str__(self):
    return "%s.%s:%s(%d)" % (self.file, self.action, self.description, self.pk)

  @classmethod
  def get_object_permission(cls, file_object, action):
    return BimFilePermission.objects.get(file=file_object, action=action)


def get_profile(user):
  """
  Caches the profile, to avoid DB queries at every call.
  """
  if hasattr(user, "_cached_userman_profile"):
    return user._cached_userman_profile
  else:
    # Lazily create profile.
    try:
      profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist, e:
      profile = create_profile_for_user(user)
    user._cached_userman_profile = profile
    return profile


# Create a user profile for the given user
def create_profile_for_user(user):
  p = UserProfile()
  p.user = user
  p.home_directory = "/user/%s" % p.user.username
  try:
    p.save()
    return p
  except:
    LOG.debug("Failed to automatically create user profile.", exc_info=True)
    return None

def get_default_user_group(**kwargs):
  default_user_group = conf.DEFAULT_USER_GROUP.get()
  if default_user_group is not None:
    group, created = auth_models.Group.objects.get_or_create(name=default_user_group)
    if created:
      group.save()

    return group

