# -*- coding:utf-8 -*-
from django.db import models
import logging

from django.db import transaction
from django.db import connection, models
from django.contrib.auth import models as auth_models
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _t
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from utils.lib.exceptions_renderable import PopupException
from utils.hadoop import cluster
from utils.models import SAMPLE_USERNAME
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
    
    user = models.ForeignKey(auth_models.User, unique=True)
    home_directory = models.CharField(editable=True, max_length=1024, null=True)
    is_usermanager = models.BooleanField(_('user manager status'), default=False,
        help_text=_('Designates that this user has the permissions to manage all user in this system'))
    is_rightmanager = models.BooleanField(_('user right status'), default=False,
        help_text=_('Designates that this user has the permissions to manage right in this system '))
    
    def get_groups(self):
        return self.user.groups.all()

    def get_group(self, proj_slug, role_slug):
        return auth_models.Group.objects.filter(groupprofile__project__slug=proj_slug,
                                                groupprofile__role__slug=role_slug).first()
        
    def has_file_permission(self, group, path, perm):
        # user must be a member of this group
        if self.user not in group.user_set.all():
            return False
        return GroupPermission.objects.filter(group=group, file_perm__file__path=path,
                                       file_perm__action__contains=perm).count() > 0

    def has_hbase_permission(self, table, perm):
        if not table or not perm:
            return False
        if self.user.is_superuser:
            return True
        if self.user.userprofile.is_rightmanager:
            return True
        for group in self.user.groups.all():
            if group_has_table_permission(group, table, perm):
                return True
            return False
     
    def get_projects(self):
        projects = set()
        groups = self.get_groups()
        for group in groups:
            projects.add(get_group_profile(group).project)
        return list(projects)

    def get_project(self, proj_slug):
        projects = self.get_projects()
        for project in projects:
            if project.slug is proj_slug:
                return project
        return None
    
    def is_project_member(self, proj_slug):
        return Project.objects.filter(groupprofile__group__user=self.user,
                                    slug=proj_slug).count() > 0

    def get_user_project_roles(self, proj_slug):
        groups = self.get_groups()
        roles = set()
        for group in groups:
            if group.groupprofile.project.slug is proj_slug:
                roles.add(group.groupprofile.role)
        return list(roles)


class Project(models.Model):
    name = models.CharField(max_length=80, unique=True)
    project_directory = models.CharField(editable=True, max_length=1024, null=True)
    created_time = models.DateTimeField(default=timezone.now)
    manager = models.ForeignKey(auth_models.User)
    slug = models.CharField(max_length=60, unique=True)


class Role(models.Model):
    name = models.CharField(max_length=80, unique=True)
    create_time = models.DateTimeField(default=timezone.now)
    role_directory = models.CharField(editable=True, max_length=1024, null=True, blank=True)
    slug = models.CharField(max_length=60, unique=True)


class GroupProfile(models.Model):
    group = models.OneToOneField(auth_models.Group)
    role = models.ForeignKey(Role)
    project = models.ForeignKey('Project')


class GroupPermission(models.Model):
    """
    Represents the permissions a group has.
    """
    group = models.ForeignKey(auth_models.Group)
    file_perm = models.ForeignKey("BimFilePermission", blank=True, null=True)
    hbase_perm = models.ForeignKey('BimHbasePermission', blank=True, null=True)

    class Meta:
        index_together = [
            ["group", "file_perm"], ["group", "hbase_perm"]
        ]

class FileInfo(models.Model):
    path = models.CharField(max_length=255, unique=True)  # 使用linux最大文件路径长度
    owner = models.ForeignKey(auth_models.User)
    group = models.ForeignKey(auth_models.Group)
    
    class Meta:
        index_together = [
            ["path"],
        ]

    def __str__(self):
        return "%s.%s:%s(%d)" % (self.path, self.owner, self.group, self.pk)


@transaction.commit_manually
def ensure_new_fileinfo(path, owner, group):
    if FileInfo.objects.filter(path=path).count() > 0:
        return
    try:
        # create file info
        file = FileInfo(path=path, owner=owner, group=group)
        file.save()

        # init file permission
        perm = BimFilePermission(file=file, action='rwx',
                                 creator=owner, description='group of file owner')
        perm.groups.add(group)
        perm.save()
    except Exception as e:
        LOG.error("user %s of group %s: file info create failed!: %s" % (owner, group, e)) 
        transaction.rollback()
    else:
        transaction.commit()


class TableInfo(models.Model):
    table = models.CharField(max_length=255, unique=True)
    creator = models.ForeignKey(auth_models.User)
    group = models.ForeignKey(auth_models.Group, help_text='the role that table belong for')
    
    class Meta:
        index_together = [
            ["table"],
        ]

    def __str__(self):
        return "%s:%s(%d)" % (self.table, self.creator, self.pk)

class BimHbasePermission(models.Model):
    """
    Set of  permissions that a hdfs file supports.
  
    For now, we only assign permissions to groups, though that may change.
    """
    groups = models.ManyToManyField(auth_models.Group, through=GroupPermission)
    table = models.ForeignKey(TableInfo)
    action = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    creator = models.ForeignKey(auth_models.User)
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        index_together = [
            ["table", "action"],
        ]
        unique_together = (("table", "action"), )

    def __str__(self):
        return "%s.%s:%s(%d)" % (self.table, self.action, self.description, self.pk)
    
    @classmethod
    def get_object_permission(cls, table, action):
        return BimHbasePermission.objects.get(table=table, action=action)


# Permission Management
class BimFilePermission(models.Model):
    """
    Set of  permissions that a hdfs file supports.
    
    For now, we only assign permissions to groups, though that may change.
    """
    file = models.ForeignKey(FileInfo)  # 使用linux最大文件路径长度
    action = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    groups = models.ManyToManyField(auth_models.Group, through=GroupPermission)
    creator = models.ForeignKey(auth_models.User)
    create_time = models.DateTimeField(default=timezone.now)
    
    class Meta:
        index_together = [
            ["file", "action"],
        ]
        unique_together = (("file", "action"), )

    def __str__(self):
        return "%s.%s:%s(%d)" % (self.file, self.action, self.description, self.pk)
    
    @classmethod
    def get_object_permission(cls, path, action):
        return BimFilePermission.objects.get(file__path=path, action=action)



    
    
def group_has_table_permission(group, table, perm):
    return GroupPermission.objects.filter(group=group, hbase_perm__table__table=table,
                                           hbase_perm__contains=perm).count() > 0


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


def get_group_profile(group):
    """
    Caches the profile, to avoid DB queries at every call.
    """
    if hasattr(group, "_cached_userman_profile"):
        return group._cached_userman_profile
    else:
        # Lazily create profile.
        try:
            profile = GroupProfile.objects.get(group=group)
        except GroupProfile.DoesNotExist, e:
            profile = create_profile_for_group(group)
        group._cached_userman_profile = profile
        return profile


def get_project_dir(project):
    if not project:
        return None
    if not project.project_directory:
        project.project_directory = '/project/%s' % project.slug
        try:
            project.save()
            return project.project_directory
        except Exception as e:
            LOG.error('Failed to automatically create project home directory', exc_info=True)
            return None
    return project.project_directory
    

# Create a group profile for the given group
def create_profile_for_group(group):
    g = GroupProfile()
    g.group = group

    try:
        g.save()
        return g
    except Exception as e:
        LOG.debug("Failed to automatically create group profile.", exc_info=True)
        return None


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


def install_sample_user():
  """
  Setup the de-activated sample user with a certain id. Do not create a user profile.
  """

  try:
    user = auth_models.User.objects.get(username=SAMPLE_USERNAME)
  except auth_models.User.DoesNotExist:
    try:
      user = auth_models.User.objects.create(username=SAMPLE_USERNAME, password='!', is_active=False, is_superuser=False, id=1100713, pk=1100713)
      LOG.info('Installed a user called "%s"' % (SAMPLE_USERNAME,))
    except Exception, e:
      LOG.info('Sample user race condition: %s' % e)
      user = auth_models.User.objects.get(username=SAMPLE_USERNAME)
      LOG.info('Sample user race condition, got: %s' % user)

  fs = cluster.get_hdfs()
  fs.do_as_user(SAMPLE_USERNAME, fs.create_home_dir)

  return user
