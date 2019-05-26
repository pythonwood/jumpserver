import datetime
import re

from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.views.generic import TemplateView, View
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri

from users.models import User
from assets.models import Asset
from terminal.models import Session
from orgs.utils import current_org

from django.http import JsonResponse
from celery.result import AsyncResult
from ops.celery.utils import get_celery_task_log_path
import json
import requests
emptyjson = {"code": 0, "state": True, "runtime": None, "data":[]}
@csrf_exempt
def site_all(request):
    response = HttpResponse()
    if request.method == 'OPTIONS':
        response = HttpResponse(content_type=None)
    elif request.method == 'POST': # or request.method == 'GET' :
        task_id = json.loads(request.body)['token'] # task_id = str(request.POST.get('token'))
        task = AsyncResult(task_id)
        # print('task_id:', task_id, flush=True) # debug
        if not task.ready(): return JsonResponse(emptyjson)
        ansible_output = {}
        ansi_escape = re.compile(r'\x1b[^m]*m')
        with open(get_celery_task_log_path(task_id)) as f:
            ip = ''
            for l in f:
                l = ansi_escape.sub('', l)
                if ' | ' in l:
                    ip = l.split(' | ')[0]
                    ansible_output[ip] = {}
                elif ': ' in l and ip:
                    k,v = tuple(l.split(': ')[:2])
                    k,v = k.strip(), v.strip()
                    if k in ['http','dns','redirect','time_connect','time_appconnect','time_pretransfer','time_starttransfer',
                        'size_download','speed_download','num_redirects','time_total' ]:
                        ansible_output[ip][k] = float(v)
                    if k in [ 'url_effective','ip']:
                        ansible_output[ip][k] = v
        use = ansible_output['14.1.98.227']
        # print('debug:', use, flush=True) # debug
        data = open(settings.BASE_DIR+'/site_all.json').read()
        jsonData = json.loads(data) #converts to a json structure
        nodeHK = jsonData['data'][55]
        nodeHK['ip'] = use['ip']
        nodeHK['url'] = json.loads(request.body)['url']
        nodeHK['token'] = task_id
        nodeHK['responescode'] = use['http']
        nodeHK['dnstime'] = int(use['dns']*1000)
        nodeHK['connecttime'] = int(use['time_connect']*1000)
        nodeHK['firstbytetime'] = int(use['time_starttransfer']*1000)
        nodeHK['filesize'] = round(use['size_download']/1024, 2)
        nodeHK['speed'] = '{:0.2f}KB/s'.format(use['speed_download']/1024) # '100MB/S'
        nodeHK['totaltime'] = int(use['time_total']*1000)
        nodeHK['downloadtime'] = nodeHK['totaltime'] - nodeHK['firstbytetime']
        response = JsonResponse(jsonData)
    else: return JsonResponse(emptyjson)
    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Allow-Headers'] = 'content-type'
    response['Access-Control-Allow-Origin'] = '*'# 'http://ce8.com:8008'
    return response

@csrf_exempt
def site_http_check(request, scheme, host):
    header = {'content-type': 'application/json', }
    data = {"hosts":["a52b250c-68b3-42bc-af11-5c3f0a4f37ab","6c601395-7785-4613-8595-0de7f4d7fde0"],"run_as":"88f3e197-3a53-4dc5-9c40-c7bd3169a84b","command":""}
    # data['command'] = 'curl -L -w "http: %{http_code}\n" -o /dev/null -s ' + scheme + '://' + host
    data['command'] = 'curl -sL ' + scheme + '://' + host + ' -o /dev/null -w "\n              http: %{http_code}\n                ip: %{remote_ip}\n               dns: %{time_namelookup}\n          redirect: %{time_redirect}\n      time_connect: %{time_connect}\n   time_appconnect: %{time_appconnect}\n  time_pretransfer: %{time_pretransfer}\ntime_starttransfer: %{time_starttransfer}\n     size_download: %{size_download}\n    speed_download: %{speed_download}\n                  ----------\n     num_redirects: %{num_redirects}\n     url_effective: %{url_effective}\n        time_total: %{time_total}\n\n"'
    # r = requests.post('{}://{}/api/ops/v1/command-executions/'.format(request.scheme, request.get_host()), headers=header, data=data)
    r = requests.post('http://127.0.0.1/api/ops/v1/command-executions/', headers=header, json=data, auth=('admin', '123qweASD')) # not data
    data = open(settings.BASE_DIR+'/ce8.com/http/qq.com.html').read() #opens the json file and saves the raw contents
    response = HttpResponse(data.replace('16a191bb-7377-4d94-b78f-2ab60ed10dd3', r.json()['id']))
    # response.set_cookie('taskid_http', r.json()['id']) # print(r.json())
    return response

@csrf_exempt
def ping_check(request, host):
    header = {'content-type': 'application/json', }
    data = {"hosts":["a52b250c-68b3-42bc-af11-5c3f0a4f37ab","6c601395-7785-4613-8595-0de7f4d7fde0"],"run_as":"88f3e197-3a53-4dc5-9c40-c7bd3169a84b","command":""}
    # data['command'] = 'curl -L -w "http: %{http_code}\n" -o /dev/null -s ' + scheme + '://' + host
    data['command'] = 'ping -w 30 -c 10 -q {}'.format(host)
    r = requests.post('http://127.0.0.1/api/ops/v1/command-executions/', headers=header, json=data, auth=('admin', '123qweASD')) # not data
    data = open(settings.BASE_DIR+'/ce8.com/ping/qq.com.html').read() #opens the json file and saves the raw contents
    response = HttpResponse(data.replace('16a191bb-7377-4d94-b78f-2ab60ed10dd3', r.json()['id']))
    # response.set_cookie('taskid_http', r.json()['id']) # print(r.json())
    return response

@csrf_exempt
def ping_all(request):
    response = HttpResponse()
    if request.method == 'OPTIONS':
        response = HttpResponse(content_type=None)
    elif request.method == 'POST': # or request.method == 'GET' :
        task_id = json.loads(request.body)['token'] # task_id = str(request.POST.get('token'))
        task = AsyncResult(task_id)
        # print('task_id:', task_id, flush=True) # debug
        if not task.ready(): return JsonResponse(emptyjson)
        ansible_output = {}
        ansi_escape = re.compile(r'\x1b[^m]*m')
        with open(get_celery_task_log_path(task_id)) as f:
            ip = ''
            for l in f:
                l = ansi_escape.sub('', l)
                if ' | ' in l:
                    ip = l.split(' | ')[0]
                    ansible_output[ip] = {}
                elif 'PING ' in l and ip:
                    ansible_output[ip]['ip'] = l.split(' (')[1].split(') ')[0]
                elif 'min/avg/max' in l and ip:
                    # rtt min/avg/max/mdev = 51.230/52.353/53.477/1.146 ms  =>  {'min': '51.230', 'avg': '52.353', 'max': '53.477', 'mdev': '1.146'}
                    kv = dict(zip(*tuple(kv.split('/') for kv in l.split() if '/' in kv ))) 
                    ansible_output[ip].update(kv)
        use = ansible_output['14.1.98.227']
        # print('debug:', use, flush=True) # debug
        data = open(settings.BASE_DIR+'/ping_all.json').read() #opens the json file and saves the raw contents
        jsonData = json.loads(data) #converts to a json structure
        nodeHK = jsonData['data'][55]
        nodeHK['ip'] = use['ip']
        nodeHK['url'] = json.loads(request.body)['url']
        nodeHK['token'] = task_id
        nodeHK['delay'] = use['avg']
        response = JsonResponse(jsonData)
    else: return JsonResponse(emptyjson)
    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Allow-Headers'] = 'content-type'
    response['Access-Control-Allow-Origin'] = '*'# 'http://ce8.com:8008'
    return response

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    session_week = None
    session_month = None
    session_month_dates = []
    session_month_dates_archive = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_org_admin:
            return redirect('assets:user-asset-list')
        if not current_org or not current_org.can_admin_by(request.user):
            return redirect('orgs:switch-a-org')
        return super(IndexView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get_user_count():
        return current_org.get_org_users().count()

    @staticmethod
    def get_asset_count():
        return Asset.objects.all().count()

    @staticmethod
    def get_online_user_count():
        return len(set(Session.objects.filter(is_finished=False).values_list('user', flat=True)))

    @staticmethod
    def get_online_session_count():
        return Session.objects.filter(is_finished=False).count()

    def get_top5_user_a_week(self):
        return self.session_week.values('user').annotate(total=Count('user')).order_by('-total')[:5]

    def get_week_login_user_count(self):
        return self.session_week.values('user').distinct().count()

    def get_week_login_asset_count(self):
        return self.session_week.count()

    def get_month_day_metrics(self):
        month_str = [d.strftime('%m-%d') for d in self.session_month_dates] or ['0']
        return month_str

    def get_month_login_metrics(self):
        data = []
        time_min = datetime.datetime.min.time()
        time_max = datetime.datetime.max.time()
        for d in self.session_month_dates:
            ds = datetime.datetime.combine(d, time_min).replace(tzinfo=timezone.get_current_timezone())
            de = datetime.datetime.combine(d, time_max).replace(tzinfo=timezone.get_current_timezone())
            data.append(self.session_month.filter(date_start__range=(ds, de)).count())
        return data

    def get_month_active_user_metrics(self):
        if self.session_month_dates_archive:
            return [q.values('user').distinct().count()
                    for q in self.session_month_dates_archive]
        else:
            return [0]

    def get_month_active_asset_metrics(self):
        if self.session_month_dates_archive:
            return [q.values('asset').distinct().count()
                    for q in self.session_month_dates_archive]
        else:
            return [0]

    def get_month_active_user_total(self):
        return self.session_month.values('user').distinct().count()

    def get_month_inactive_user_total(self):
        return current_org.get_org_users().count() - self.get_month_active_user_total()

    def get_month_active_asset_total(self):
        return self.session_month.values('asset').distinct().count()

    def get_month_inactive_asset_total(self):
        return Asset.objects.all().count() - self.get_month_active_asset_total()

    @staticmethod
    def get_user_disabled_total():
        return current_org.get_org_users().filter(is_active=False).count()

    @staticmethod
    def get_asset_disabled_total():
        return Asset.objects.filter(is_active=False).count()

    def get_week_top10_asset(self):
        assets = list(self.session_week.values('asset').annotate(total=Count('asset')).order_by('-total')[:10])
        for asset in assets:
            last_login = self.session_week.filter(asset=asset["asset"]).order_by('date_start').last()
            asset['last'] = last_login
        return assets

    def get_week_top10_user(self):
        users = list(self.session_week.values('user').annotate(
            total=Count('asset')).order_by('-total')[:10])
        for user in users:
            last_login = self.session_week.filter(user=user["user"]).order_by('date_start').last()
            user['last'] = last_login
        return users

    def get_last10_sessions(self):
        sessions = self.session_week.order_by('-date_start')[:10]
        for session in sessions:
            try:
                session.avatar_url = User.objects.get(username=session.user).avatar_url()
            except User.DoesNotExist:
                session.avatar_url = User.objects.first().avatar_url()
        return sessions

    def get_context_data(self, **kwargs):
        week_ago = timezone.now() - timezone.timedelta(weeks=1)
        month_ago = timezone.now() - timezone.timedelta(days=30)
        self.session_week = Session.objects.filter(date_start__gt=week_ago)
        self.session_month = Session.objects.filter(date_start__gt=month_ago)
        self.session_month_dates = self.session_month.dates('date_start', 'day')

        self.session_month_dates_archive = []
        time_min = datetime.datetime.min.time()
        time_max = datetime.datetime.max.time()

        for d in self.session_month_dates:
            ds = datetime.datetime.combine(d, time_min).replace(
                tzinfo=timezone.get_current_timezone())
            de = datetime.datetime.combine(d, time_max).replace(
                tzinfo=timezone.get_current_timezone())
            self.session_month_dates_archive.append(
                self.session_month.filter(date_start__range=(ds, de)))

        context = {
            'assets_count': self.get_asset_count(),
            'users_count': self.get_user_count(),
            'online_user_count': self.get_online_user_count(),
            'online_asset_count': self.get_online_session_count(),
            'user_visit_count_weekly': self.get_week_login_user_count(),
            'asset_visit_count_weekly': self.get_week_login_asset_count(),
            'user_visit_count_top_five': self.get_top5_user_a_week(),
            'month_str': self.get_month_day_metrics(),
            'month_total_visit_count': self.get_month_login_metrics(),
            'month_user': self.get_month_active_user_metrics(),
            'mouth_asset': self.get_month_active_asset_metrics(),
            'month_user_active': self.get_month_active_user_total(),
            'month_user_inactive': self.get_month_inactive_user_total(),
            'month_user_disabled': self.get_user_disabled_total(),
            'month_asset_active': self.get_month_active_asset_total(),
            'month_asset_inactive': self.get_month_inactive_asset_total(),
            'month_asset_disabled': self.get_asset_disabled_total(),
            'week_asset_hot_ten': self.get_week_top10_asset(),
            'last_login_ten': self.get_last10_sessions(),
            'week_user_hot_ten': self.get_week_top10_user(),
        }

        kwargs.update(context)
        return super(IndexView, self).get_context_data(**kwargs)


class LunaView(View):
    def get(self, request):
        msg = _("<div>Luna is a separately deployed program, you need to deploy Luna, coco, configure nginx for url distribution,</div> "
                "</div>If you see this page, prove that you are not accessing the nginx listening port. Good luck.</div>")
        return HttpResponse(msg)


class I18NView(View):
    def get(self, request, lang):
        referer_url = request.META.get('HTTP_REFERER', '/')
        response = HttpResponseRedirect(referer_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
        return response


api_url_pattern = re.compile(r'^/api/(?P<version>\w+)/(?P<app>\w+)/(?P<extra>.*)$')


class HttpResponseTemporaryRedirect(HttpResponse):
    status_code = 307

    def __init__(self, redirect_to):
        HttpResponse.__init__(self)
        self['Location'] = iri_to_uri(redirect_to)


@csrf_exempt
def redirect_format_api(request, *args, **kwargs):
    _path, query = request.path, request.GET.urlencode()
    matched = api_url_pattern.match(_path)
    if matched:
        version, app, extra = matched.groups()
        _path = '/api/{app}/{version}/{extra}?{query}'.format(**{
            "app": app, "version": version, "extra": extra,
            "query": query
        })
        return HttpResponseTemporaryRedirect(_path)
    else:
        return Response({"msg": "Redirect url failed: {}".format(_path)}, status=404)
