# coding=utf-8
#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import base64
import json
import logging
import re
import StringIO
import urllib

from avro import datafile, io

from django.utils.translation import ugettext as _
from django.conf import settings
from utils.lib.django_util import PopupException, JsonResponse, render

from hbase import conf
from hbase.settings import DJANGO_APPS
from hbase.api import HbaseApi
from hbase.management.commands import hbase_setup
from server.hbase_lib import get_thrift_type
from admin.models import ensuire_table_info, get_group_table_permission, get_profile

LOG = logging.getLogger(__name__)


def has_write_access(user):
  return user.is_superuser or user.has_hue_permission(action="write", app=DJANGO_APPS[0])

def app(request, proj_slug, role_slug):
    # should give a table name
    # perm = get_group_table_permission(request.group, table)

  return render('app.mako', request, {
    'can_write': has_write_access(request.user), 
    # 'can_wirte': settings.HBASE_INSERT_PERM in perm,
    # 'can_delete': settings.HBASE_DELETE_PERM in perm
  })


def action_perm_required(action):
  for item in HbaseApi.HBASE_ACTION_PERM_REQUEST.iterkeys():
      pattern = re.compile(item)
      match = pattern.match(action)
      if match:
          return HbaseApi.HBASE_ACTION_PERM_REQUEST.get(item)
  return None
      
        
# action/cluster/arg1/arg2/arg3...
def api_router(request, proj_slug, role_slug, url): # On split, deserialize anything

  def safe_json_load(raw):
    try:
      return json.loads(re.sub(r'(?:\")([0-9]+)(?:\")', r'\1', str(raw)))
    except:
      return raw

  def deserialize(data):
    if type(data) == dict:
      special_type = get_thrift_type(data.pop('hue-thrift-type', ''))
      if special_type:
        return special_type(data)

    if hasattr(data, "__iter__"):
      for i, item in enumerate(data):
        data[i] = deserialize(item) # Sets local binding, needs to set in data
    return data

  decoded_url_params = [urllib.unquote(arg) for arg in re.split(r'(?<!\\)/', url.strip('/'))]
  url_params = [safe_json_load((arg, request.POST.get(arg[0:16], arg))[arg[0:15] == 'hbase-post-key-'])
                for arg in decoded_url_params] # Deserialize later

   # 操作权限验证
  if settings.NEED_PERMISSION:
    action = url_params[0]
    need_perm = action_perm_required(action)
    tablename = url_params[2] if len(url_params) > 2 else None
    if not get_profile(request.user).has_hbase_permission(request.group, tablename, need_perm):
      LOG.info('Permission deny! : user %s try to %s table %s' %
                            (request.user.username, action, tablename))
      return JsonResponse({'error': 'Permission deny!'}, status=403)
 
#   # create or clear table info when needed
#   ensuire_table_info(request.user, tablename, request.group, action)

  if request.POST.get('dest', False):
    url_params += [request.FILES.get(request.REQUEST.get('dest'))]
    
  # do
  result = HbaseApi(request.user).query(*url_params)
  
  # create table info when call method createTable
  if settings.NEED_PERMISSION and action == 'createTable':
    ensuire_table_info(request.user, tablename, request.group, action)

  return api_dump(result)

def api_dump(response):
  ignored_fields = ('thrift_spec', '__.+__')
  trunc_limit = conf.TRUNCATE_LIMIT.get()

  def clean(data):
    try:
      json.dumps(data)
      return data
    except:
      cleaned = {}
      lim = [0]
      if isinstance(data, str): # Not JSON dumpable, meaning some sort of bytestring or byte data
        #detect if avro file
        if(data[:3] == '\x4F\x62\x6A'):
          #write data to file in memory
          output = StringIO.StringIO()
          output.write(data)

          #read and parse avro
          rec_reader = io.DatumReader()
          df_reader = datafile.DataFileReader(output, rec_reader)
          return json.dumps(clean([record for record in df_reader]))
        return base64.b64encode(data)

      if hasattr(data, "__iter__"):
        if type(data) is dict:
          for i in data:
            cleaned[i] = clean(data[i])
        elif type(data) is list:
          cleaned = []
          for i, item in enumerate(data):
            cleaned += [clean(item)]
        else:
          for i, item in enumerate(data):
            cleaned[i] = clean(item)
      else:
        for key in dir(data):
          value = getattr(data, key)
          if value is not None and not hasattr(value, '__call__') and sum([int(bool(re.search(ignore, key)))
                                                                           for ignore in ignored_fields]) == 0:
            cleaned[key] = clean(value)
      return cleaned

  return JsonResponse({
    'data': clean(response),
    'truncated': True,
    'limit': trunc_limit,
    })


def install_examples(request):
  result = {'status': -1, 'message': ''}

  if request.method != 'POST':
    result['message'] = _('A POST request is required.')
  else:
    try:
      hbase_setup.Command().handle(user=request.user)
      result['status'] = 0
    except Exception, e:
      LOG.exception(e)
      result['message'] = str(e)

  return JsonResponse(result)
