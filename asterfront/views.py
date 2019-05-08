# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, UpdateView, DeleteView, FormView, CreateView
from django.db.models import Count, OuterRef, Subquery
from django.utils.timesince import timesince
from django.http import JsonResponse
from models import *
from datetime import datetime
from helpers import views as helpers_views
from django.conf import settings
import re
from ami import AsteriskAmi
from django.contrib.auth import authenticate, login


DEFAULT_QUEUE = ''


def _has_ast_permissions(user):
    return user.has_perm('asterfront.add_blacklisted')


def add_to_blacklist(number, comment='Null'):
    number = '7'.join(re.findall('[0-9]', number))[-10:]
    response = AsteriskAmi().put_db('blacklist', number, comment)


def agent_status(key):
    switch = {
        '1' : 'Свободен',
        '2' : '<font color="orange">Разговаривает</font>',
        '3' : '<font color="red">Занято</font>',
        '4' : 'Не определено',
        '5' : '<font color="red">Не доступен</font>',
        '6' : '<font color="blue">Звонит</font>',
    }
    return switch.get(key, 'Не определено')


def pause_status(key):
    switch = {
        '0' : '',
        '1' : '<span class="glyphicon glyphicon-pause"></span>'
    }
    return switch.get(key, 'Не определено')


def aster_queuestatus(queue_name=DEFAULT_QUEUE):
    '''get QueueStatus from asterisk and returns it in dict'''
    response = AsteriskAmi().get_response(dict(Action='QueueStatus'))
    queue_data = {}
    for k in response.findAll('generic'):
        if k.get('event') == 'QueueMember':
            if k.get('queue') == queue_name:
                if not queue_data.has_key('members'):
                    queue_data['members'] = []
                pause = k.get('paused')
                status = k.get('status')
                agent = re.search('(\d+)', k.get('name')).group(0)
                last_call_time = k.get('lastcall')
                if last_call_time <> '0':
                    last_ago = timesince(datetime.fromtimestamp(int(k.get('lastcall'))))
                else:
                    last_ago = ""
                if pause=='0' and status=='1':
                    agent='<font color="green">%s</font>' % agent
                else:
                    agent='<font color="red">%s</font>' % agent
                queue_data['members'].append({agent: {
                    'pause': pause_status(k.get('paused')),
                    'status' : agent_status(k.get('status')),
                    'last' : last_ago,
                    'calls' : k.get('callstaken')}})
        elif k.get('event') == 'QueueEntry':
            if k.get('queue') == queue_name:
                if not queue_data.has_key('calls'):
                    queue_data['calls'] = []
                queue_data['calls'].append({k.get('calleridnum') : {
                                                'place': k.get('position'),
                                                'wait': k.get('wait')}
                                                })
        elif k.get('event') == 'QueueParams':
            if k.get('queue') == queue_name:
                if not queue_data.has_key('queue_info'):
                    queue_data['queue_info'] = {}
                queue_data['queue_info'] = {'SLA': k.get('servicelevelperf'),
                                            'Среднее время ожидания': k.get('holdtime'),
                                            'Среднее время разговора': k.get('talktime')
                                            }
    return queue_data


def get_abandoned(queue_name=DEFAULT_QUEUE):
    from datetime import datetime
    import pytz
    utc = pytz.UTC
    date = utc.localize(datetime.now())
    date = date.replace(hour=0, minute=0, second=0)
    abandoned = QueueLog.objects.using('asterisk').filter(event='ABANDON', queuename=queue_name, time__gte=date)
    hang = QueueLog.objects.using('asterisk').filter(event='COMPLETEAGENT', queuename=queue_name, time__gte=date, data2__iregex=r'^[0-5]$')
    return abandoned, hang


@helpers_views.LoginRequired(login_url=settings.LOGIN_URL)
class LoginRequiredTemplateView(TemplateView):

    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredTemplateView, self).dispatch(*args, **kwargs)


class Main(LoginRequiredTemplateView):
     template_name = 'asterfront/main_asterfront.html'


class QueueStats(LoginRequiredTemplateView):
    template_name = 'asterfront/queue_status.html'

    def get_context_data(self, **kwargs):

        context = super(QueueStats, self).get_context_data(**kwargs)
        try:
            queue_name = self.kwargs['queue_name']
            context['data'] = aster_queuestatus(queue_name)
        except:
            context['data'] = aster_queuestatus(DEFAULT_QUEUE)
        return context

    def get(self, request, **kwargs):
        queue = request.GET.get('queue')
        if queue:
            return self.render_to_response(self.get_context_data(queue_name=queue), **kwargs)
        else:
             return self.render_to_response(self.get_context_data(), **kwargs)


class AbandonedCallsView(LoginRequiredTemplateView):
    template_name = 'asterfront/abandon.html'

    def get_context_data(self, **kwargs):
        context = super(AbandonedCallsView, self).get_context_data(**kwargs)
        context['abandon'], context['hang'] = get_abandoned()
        return context


class OutCalls(LoginRequiredTemplateView):
    template_name = 'asterfront/outcalls.html'

    def get_context_data(self, **kwargs):
        from datetime import datetime
        import pytz
        utc = pytz.UTC
        date = utc.localize(datetime.now())
        date = date.replace(hour=0, minute=0, second=0)
        context = super(OutCalls, self).get_context_data(**kwargs)
        calls = Cdr.objects.using('asterisk').filter(calldate__gte=date, src__iregex=r'^47..$').exclude(dst__contains='*').values('src').annotate(Count('src'))
        context['calls'] = calls
        return context


class BlackNumber(CreateView):
    model = BlackListed
    fields = ['number', 'cause']
    success_url = 'addtoblack'

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super(BlackNumber, self).form_valid(form)


class AjaxableResponseMixin(object):
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


class LoginForm(TemplateView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super(LoginForm, self).get_context_data(**kwargs)
        context['next'] = getattr(self.request, self.request.method).get('next', '/')
        self.kwargs['next'] = context['next']
        return context

    def post(self, request, *args, **kwargs):
        username_ = request.POST.get('username')
        password_ = request.POST.get('password')
        user_ = authenticate(username=username_, password=password_)
        next_page = self.get_context_data()['next']
        print "hello"
        if next_page == "":
            next_page = "/"
        if user_:
            print user_
            if user_.is_active:
                print "yes"
                login(request, user_)
                return redirect(next_page)
            else:
                return redirect('/')
        error = 'Неверный логин или пароль!'
        return render(self.request, self.template_name, {'errors': [error]})
