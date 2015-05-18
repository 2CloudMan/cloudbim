# -*- coding:utf-8 -*-
from django.db import models
import logging
from django.conf import settings
from django.db import transaction
from django.db import connection, models
from django.contrib.auth import models as auth_models
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _t
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text
from django.contrib.admin.models import DELETION, ADDITION, CHANGE

from utils.lib.exceptions_renderable import PopupException
from utils.hadoop import cluster

import conf
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.
LOG = logging.getLogger(__name__)


class UserLog(models.Model):
    action_time = models.DateTimeField(_('action time'), auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.TextField(_('object id'), blank=True, null=True)
    object_repr = models.CharField(_('object repr'), max_length=200)
    action_flag = models.PositiveSmallIntegerField(_('action flag'))
    change_message = models.TextField(_('change message'), blank=True)
    

class UserProfile(models.Model):
    user = models.ForeignKey(auth_models.User, unique=True)
    home_directory = models.CharField(editable=True, max_length=1024, null=True)
    is_usermanager = models.BooleanField(_('user manager status'), default=False,
        help_text=_('Designates that this user has the permissions to manage all user in this system'))
    is_rightmanager = models.BooleanField(_('user right status'), default=False,
        help_text=_('Designates that this user has the permissions to manage right in this system '))
    
    def __str__(self):
        return self.user.username
        
    def get_groups(self):
        return self.user.groups.all()

    def get_group(self, proj_slug, role_slug):
        return auth_models.Group.objects.filter(groupprofile__project__slug=proj_slug,
                                                groupprofile__role__slug=role_slug).first()
        
    def has_file_permission(self, group, path, perm):
        # user must be a member of this group
        if not group or not path or not perm:
            return False

        if self.user.is_superuser:
            return True

        if path.endswith('/'):
            path = path[:-1]

        if perm in 'r' and get_project_dir(group.groupprofile.project) == path:
            return True
        
        if get_proj_role_path(group.groupprofile.project, group.groupprofile.role) == path:
            return True

        perm = BimFilePermission.objects.filter(file__path=path,
                                               action__contains=perm).first()

        if not perm:
            return False
        else:
            return perm.groups.filter(name=group.name).exists()

    def is_table_owner(self, table):
        return TableInfo.objects.filter(creator=self.user, table=table).exists()
    
    def has_hbase_permission(self, group, table, perm):
        if perm == True:
            return True

        if self.is_table_owner(table):
            return True

        if perm in [settings.HBASE_INSERT_PERM, settings.HBASE_QUERY_PERM,
                       settings.HBASE_DELETE_PERM]:
            if self.has_hbase_data_permission(group, table, perm):
                return True

        return False
            
    def has_hbase_data_permission(self, group, table, perm):
        if not table or not perm:
            return False
        # 前期测试，功能完成后删除
#         if self.user.is_superuser:
#             return True
        if group_has_table_permission(group, table, perm):
            return True
        
        return False


    def get_projects(self):
        projects = set()
        groups = self.get_groups()
        for group in groups:
            proj =  get_group_profile(group).project
            if not proj:
                continue
            projects.add(proj)
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
            profile = get_group_profile(group)
            if profile.project.slug is proj_slug:
                roles.add(profile.role)
        return list(roles)

    def get_user_first_role(self, proj_slug):
        first_grp = self.user.groups.filter(groupprofile__project__slug=proj_slug).first()
        if first_grp:
            return get_group_profile(first_grp).role
        return None

    def userlog_download(self, object, message):
        """
        Log that an object has been successfully added.

        The default implementation creates an  user Log record object.
        """
        DOWNLOAD = 4
        ul = UserLog(
            user_id=self.user.pk,
            content_type_id=ContentType.objects.get_for_model(object).pk,
            object_id=object.pk,
            object_repr=force_text(object),
            action_flag=DOWNLOAD,
            change_message = message
        )
        ul.save()

    
    def userlog_addition(self, object, message):
        """
        Log that an object has been successfully added.

        The default implementation creates an  user Log record object.
        """
        ul = UserLog(
            user_id=self.user.pk,
            content_type_id=ContentType.objects.get_for_model(object).pk,
            object_id=object.pk,
            object_repr=force_text(object),
            action_flag=ADDITION,
            change_message = message
        )
        ul.save()

    def userlog_change(self, object, message):
        """
        Log that an object has been successfully changed.

        The default implementation creates an user Log record object.
        """
        ul = UserLog(
            user_id=self.user.pk,
            content_type_id=ContentType.objects.get_for_model(object).pk,
            object_id=object.pk,
            object_repr=force_text(object),
            action_flag=CHANGE,
            change_message=message
        )
        ul.save()

    def userlog_deletion(self, object, message):
        """
        Log that an object will be deleted. Note that this method is called
        before the deletion.

        The default implementation creates an user Log record object.
        """
        ul = UserLog(
            user_id=self.user.pk,
            content_type_id=ContentType.objects.get_for_model(object).pk,
            object_id=object.pk,
            object_repr=force_text(object),
            action_flag=DELETION,
            change_message=message
        )
        ul.save()

    def get_userlog(self, query, type):
        log = UserLog.objects.filter(user_id=self.user.pk)
        if query:
            log = log.filter(object_repr__contains=query)

        type = ContentType.objects.filter(model=type).first()

        if not type:
            return []
        log = log.filter(content_type_id=type.id)

        return log
        
class Project(models.Model):
    # 项目名称，最大长度为80个字符，值唯一
    name = models.CharField(max_length=80, unique=True)
    # 项目目录，最大长度为1024个字符，可空,值唯一
    project_directory = models.CharField(editable=True, max_length=255, null=True, unique=True,
                                         help_text=('it must under directory %s' % settings.HADOOP_PROJECT_DIR))
    # 项目创建时间，默认值为项目创建时的时间
    created_time = models.DateTimeField(default=timezone.now)
    # 项目管理员，外键依赖于用户表
    manager = models.ForeignKey(auth_models.User)
    # 项目标识，用于唯一标记一个项目
    slug = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return "%s:%s" % (self.name, self.slug)


class Role(models.Model):
    # 角色名，最大长度为80个字符，值唯一
    name = models.CharField(max_length=80, unique=True)
    # 角色创建时间，默认值为项目创建时的时间
    create_time = models.DateTimeField(default=timezone.now)
    # 角色目录，定义角色在项目下的具体目录名称，最大长度1024个字符，可空
    role_directory = models.CharField(editable=True, max_length=1024, null=True, blank=True)
    # 角色标识，用于唯一标识一个角色
    slug = models.CharField(max_length=60, unique=True)
    
    def __str__(self):
        return "%s:%s" % (self.name, self.slug)


class GroupProfile(models.Model):
    # 与组表一对一对应
    group = models.OneToOneField(auth_models.Group)
    # 与role表外键依赖， 可空
    role = models.ForeignKey(Role, null=True, blank=True)
    # 与项目表外键依赖， 可空
    project = models.ForeignKey('Project', null=True, blank=True)
    
    def __str__(self):
        return self.group.name


class TableInfo(models.Model):
    # 表格名称， 最大限制长度为255个字符，值唯一
    table = models.CharField(max_length=255, unique=True)
    # 表格的创建名称，与用户表外键依赖
    creator = models.ForeignKey(auth_models.User)
    # 创建者所属的组，与组表外键依赖
    group = models.ForeignKey(auth_models.Group, help_text='the role that table belong for')

    class Meta:
        index_together = [
            ["table"],
        ]

    def __str__(self):
        return self.table


FILE_PERM_CHOICES = (
    ('r', 'can read'),
    ('w', 'can write'),
    ('rw', 'both read and write'),
)


TABLE_PERM_CHOICES = (
    ('q', 'can query data'),
    ('qd', 'can query and delete data'),
    ('qi', 'can query and insert'),
    ('qdi', 'can query, delete and inset'),
)


class BimHbasePermission(models.Model):
    """
    Set of  permissions that a hdfs file supports.
  
    For now, we only assign permissions to groups, though that may change.
    """
    # 外键，与表格信息表存在外键依赖
    table = models.ForeignKey(TableInfo)
    # 操作，定义了可操作的选项，最大限制长度为255个字符
    action = models.CharField(max_length=255, choices=TABLE_PERM_CHOICES)
    # 描述，最大限制长度为255个字符
    description = models.CharField(max_length=255, blank=True)
    # 定义与组表的多对多关系
    groups = models.ManyToManyField(auth_models.Group) 
    # 创建者，外键依赖，与用户是多对一关系
    creator = models.ForeignKey(auth_models.User)
    # 记录创建时间，默认值为创建记录的系统时间
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        index_together = [
            ["table", "action"],
        ]
        unique_together = (("table", "action"), )

    def __str__(self):
        return "%s:%s" % (self.table, self.action)
    
    @classmethod
    def get_object_permission(cls, table, action):
        return BimHbasePermission.objects.get(table=table, action=action)


class FileInfo(models.Model):
    path = models.CharField(max_length=255, unique=True)  # 使用linux最大文件路径长度
    owner = models.ForeignKey(auth_models.User)
    group = models.ForeignKey(auth_models.Group)

    class Meta:
        index_together = [
            ["path"],
        ]

    def __str__(self):
        return self.path


# Permission Management
class BimFilePermission(models.Model):
    """
    Set of  permissions that a hdfs file supports.
    
    For now, we only assign permissions to groups, though that may change.
    """
    file = models.ForeignKey(FileInfo)  # 使用linux最大文件路径长度
    action = models.CharField(max_length=100, choices=FILE_PERM_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    groups = models.ManyToManyField(auth_models.Group) # , through=GroupPermission
    creator = models.ForeignKey(auth_models.User)
    create_time = models.DateTimeField(default=timezone.now)
    
    class Meta:
        index_together = [
            ["file", "action"],
        ]
        unique_together = (("file", "action"), )

    def __str__(self):
        return "%s:%s" % (self.file, self.action)
    
    @classmethod
    def get_object_permission(cls, path, action):
        return BimFilePermission.objects.get(file__path=path, action=action)

@transaction.commit_manually
def clear_file_info(request, path):
    try:
        # 删除文件相关权限
        BimFilePermission.objects.filter(file__path=path).delete()

        # 获取文件信息
        file = FileInfo.objects.get(path=path)

        # 添加用户日志
        msg = 'file delete'
        get_profile(request.user).userlog_deletion(request, file, msg)
        
        # 删除文件信息
        file.delete()
    except Exception as e:
        LOG.error("File info clear failed! ", exc_info=e) 
        transaction.rollback()
    else:
        transaction.commit()

@transaction.commit_manually
def ensure_new_fileinfo(path, request, is_dir=True):
    if FileInfo.objects.filter(path=path).exists():
        return

    try:
        # create file info
        file = FileInfo(path=path, owner=request.user, group=request.group)
        file.save()

        # init file permission
        # 安装创建的文件类型来初始化权限
        if is_dir:
            perm = BimFilePermission(file=file, action=settings.INIT_DIR_PERM_OWN_GRP,
                                     creator=request.user, description='group of file owner')
        else:
            perm = BimFilePermission(file=file, action=settings.INIT_FILE_PERM_OWN_GRP,
                                     creator=request.user, description='group of file owner')

        perm.save()
        perm.groups.add(request.group)
        perm.save()
        
        # 添加用户日志
        msg = 'file add'
        get_profile(request.user).userlog_addition(request, file, msg)
    except Exception as e:
        LOG.error("user %s of group %s: file info create failed!: %s" % (request.user, request.group, e)) 
        transaction.rollback()
    else:
        transaction.commit()


def get_group_table_permission(group, table):
    if not group or not table:
        return ''
    
    perm = BimHbasePermission.objects.filter(table__table=table)
    
    if perm:
        if perm.groups.filter(name=group.name).exists():
            return perm.action
    return ''
    

def group_has_table_permission(group, table, perm):
    if not group or not table or not perm:
        return False

    perm = BimHbasePermission.objects.filter(table__table=table,
                                           action__contains=perm).first()
      
    if perm:
        return perm.groups.filter(name=group.name).exists()
    return False


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


def get_user_proj_roles_info(user, proj):
    result = dict(project={}, roles=[])
    if not proj or not isinstance(user, auth_models.User) or not isinstance(proj, Project):
        return result

    groups = user.groups.all().filter(groupprofile__project=proj)
    GroupProfile.objects.filter(group__in=groups, project=proj).all()
    roles = []
    for group in groups:
        roles.append(get_role_info(group.groupprofile.role))

    project = get_proj_info(proj)
    return project, roles


def get_proj_info(proj):
    if not proj:
        return {} 
    return {
            'name': proj.name,
            'slug': proj.slug,
            'create_time': proj.created_time,
            'home_directory': proj.project_directory
            }


def get_role_info(role):
    if not role:
        return {}
    return {
            'name': role.name,
            'slug': role.slug,
            'code': role.pk
            }

def get_project_dir(project):
    if not project:
        return None
    if not project.project_directory:
        project.project_directory = settings.HADOOP_PROJECT_DIR + '%s' % project.slug
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


def get_proj_role_path(project, role):
    if not project or not role:
        return ''
    proj_dir = get_project_dir(project)
    role_dir = role.role_directory
    path = proj_dir + (role_dir if role_dir and role_dir.startswith('/') else '/%s' % role.slug)
    return path

def ensure_proj_role_directory(fs, project, role):
    path = get_proj_role_path(project, role)
    if path:
        fs.do_as_superuser(fs.create_role_dir, path)

# clear table info 
@transaction.commit_manually
def clear_table_info(tablename):
    try:
        # 删除相关权限
        BimHbasePermission.objects.filter(table__table=tablename).delete()
        
        # 删除相关表格信息
        TableInfo.objects.filter(table=tablename).delete()
    except Exception as e:
        LOG.error("Table info clear failed! ", exc_info=e) 
        transaction.rollback()
    else:
        transaction.commit()


# create table info when needed
@transaction.commit_manually
def ensuire_table_info(user, tablename, group, action):
    if action == 'createTable':
        try:
            # create table info
            table = TableInfo(table=tablename, creator=user, group=group)
            table.save()
            
            # create permission
            perm = BimHbasePermission(table=table, action='qi', creator=user)
            perm.save()

            perm.groups.add(group)
            perm.save()
            LOG.info('user %s of group %s: table %s  info created!' % (user.username, group.name, tablename))
        except Exception as e:
            LOG.error("user %s of group %s: table info create failed!: %s" % (user.username, group.name, e)) 
            print e
            transaction.rollback()
        else:
            transaction.commit()
    
    # 删除表格信息的操作
    pass

       
  
