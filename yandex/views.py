#-*- coding: utf-8 -*-

import datetime
import json
from urllib.parse import quote

import simplejson
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import auth
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.context_processors import csrf

from yandex.api_yandex import *
from .models import InfoEmail, Alliases, Maillist, Forward, ExcludeEmail
from .forms import AddEmail, SetForward, DelForward, LoginForm, EditUser, AddExcludEmail
from urllib.request import urlopen, Request
import xml.etree.ElementTree as ET
import time
from django.views.decorators.csrf import csrf_protect

class YandexUpdate(object):

    _request = {}

    def pars(self):
        print('Run pars')
        args = {}

        list_email = URL_API + URL_GET_LIST
        loads = (urlopen(list_email).read()).decode('utf-8')
        j = json.loads(str(loads))

        test = []
        page = 1
        if j['pages'] >= 1:  # Если страниц больше 1
            for i in range(1, j['pages']+1):
                page = i
                list_email = URL_API + URL_GET_LIST_PAGE % (TOKEN, DOMAIN, page)
                loads = (urlopen(list_email).read()).decode('utf-8')
                j = json.loads(str(loads))
                for account in j['accounts']:
                    forvard_list = URL_API + URL_GET_FORVARD_LIST % (token, account['login'])

                    link = ET.parse(urlopen(forvard_list))
                    par = link.getroot()

                    if par.find('ok') != None:
                        id_fw = []
                        forward = []
                        copy = []
                        filter_param = []
                        enabled_forw = []

                        for elem in par.findall('ok/filters/filter'):
                            id_fw.append(elem.find('id').text)
                            forward.append(elem.find('forward').text)
                            copy.append(elem.find('copy').text)
                            filter_param.append(elem.find('filter_param').text)
                            enabled_forw.append(elem.find('enabled').text)
                        test.append({
                            'logins': account['login'].split('@')[0],
                            'domain': j['domain'],
                            'maillist': account['maillist'],
                            'sex': str(account['sex']),
                            'birth_date': str(account['birth_date']),
                            'iname': str(account['iname']),
                            'uid': str(account['uid']),
                            'enabled': account['enabled'],
                            'fname': str(account['fname']),
                            'ready': str(account['ready']),
                            'aliases': account['aliases'],
                            'hintq': account['hintq'],

                            'id_fw': id_fw,
                            'forward': forward,
                            'copy': copy,
                            'filter_param': filter_param,
                            'enabled_forw': enabled_forw,
                        })
                    else:
                        test.append({
                            'logins': account['login'].split('@')[0],
                            'maillist': account['maillist'],
                            'sex': str(account['sex']),
                            'birth_date': str(account['birth_date']),
                            'iname': str(account['iname']),
                            'uid': str(account['uid']),
                            'enabled': account['enabled'],
                            'fname': str(account['fname']),
                            'ready': str(account['ready']),
                            'aliases': account['aliases'],

                            'id_fw': None,
                            'forward': None,
                            'copy': None,
                            'filter_param': None,
                            'enabled_forw': None,
                        })
        args['accounts'] = test
        domain = MailAdmin.objects.get(user_id = 1).id
        YandexUpdate.verification_forvard(args['accounts'])
        YandexUpdate.save(domain, test)
        MailAdmin.objects.filter(user = 1).update(last_update_db=timezone.now())

    def save(domain, *args):
        print('Save')
        for account in args:
            for ac in account:
                # print(ac)
                if not InfoEmail.objects.filter(login=ac['logins']):
                    inf_eml = InfoEmail.objects.create(
                        login=ac['logins'],
                        domain_id=domain,
                        sex=ac['sex'],
                        birth_date=ac['birth_date'],
                        iname=ac['iname'],
                        fname=ac['fname'],
                        uid=ac['uid'],
                        enabled=ac['enabled'],
                        ready=ac['ready'],
                        hintq=ac['hintq'],
                    )
                    inf_eml.save()

                    allis = Alliases.objects.create(
                        name=ac['aliases'],
                        info_email_id=inf_eml.id
                    )
                    allis.save()

                    mlst = Maillist.objects.create(
                        name=ac['aliases'],
                        infoemail_id=inf_eml.id
                    )
                    mlst.save()

                    # Переадресация
                    forvard_list = URL_API + URL_GET_FORVARD_LIST % (token, ac['logins'])
                    link = ET.parse(urlopen(forvard_list))
                    par = link.getroot()

                    if par.find('ok') != None:
                        id_fw = []
                        forward = []
                        copy = []
                        filter_params = []

                        for elem in par.findall('ok/filters/filter'):
                            id_fw.append(elem.find('id').text)
                            forward.append(elem.find('forward').text)
                            copy.append(elem.find('copy').text)
                            filter_params.append(elem.find('filter_param').text)

                            if not Forward.objects.filter(id_fw=elem.find('id').text):
                                f = Forward.objects.create(
                                    info_email_id=inf_eml.id,
                                    id_fw=elem.find('id').text,
                                    forwards=elem.find('forward').text,
                                    copies=elem.find('copy').text,
                                    filter_param=elem.find('filter_param').text,
                                    enabled_forw=elem.find('enabled').text
                                )
                                f.save()

                else: #Обновляем
                    InfoEmail.objects.filter(login=ac['logins']).update(
                        login=ac['logins'],
                        domain_id=domain,
                        sex=ac['sex'],
                        birth_date=ac['birth_date'],
                        iname=ac['iname'],
                        fname=ac['fname'],
                        uid=ac['uid'],
                        enabled=ac['enabled'],
                        ready=ac['ready'],
                        hintq=ac['hintq'],
                    )
                    # inf_eml.save()

                    Alliases.objects.filter(info_email__login=ac['logins']).update(
                        name=ac['aliases'],
                        # info_email_id=inf_eml.id
                    )
                    # allis.save()

                    Maillist.objects.filter(infoemail__login=ac['logins']).update(
                        name=ac['aliases'],
                        # infoemail_id=inf_eml.id
                    )
                    # mlst.save()

                    # Переадресация
                    forvard_list = URL_API + URL_GET_FORVARD_LIST % (token, ac['logins'])
                    link = ET.parse(urlopen(forvard_list))
                    par = link.getroot()

                    if par.find('ok') != None:
                        id_fw = []
                        forward = []
                        copy = []
                        filter_params = []

                        for elem in par.findall('ok/filters/filter'):
                            id_fw.append(elem.find('id').text)
                            forward.append(elem.find('forward').text)
                            copy.append(elem.find('copy').text)
                            filter_params.append(elem.find('filter_param').text)

                            if not Forward.objects.filter(id_fw=elem.find('id').text):
                                #print(InfoEmail.objects.filter(login = ac['logins']).get().id)
                                f = Forward.objects.create(
                                    info_email_id=InfoEmail.objects.filter(login = ac['logins']).get().id,
                                    id_fw=elem.find('id').text,
                                    forwards=elem.find('forward').text,
                                    copies=elem.find('copy').text,
                                    filter_param=elem.find('filter_param').text,
                                    enabled_forw=elem.find('enabled').text
                                )
                                f.save()

    def update_forward(*args):
        print('update_forward')
        for log in args:
            forvard_list = URL_API+ URL_GET_FORVARD_LIST % (token, log)
            link = ET.parse(urlopen(forvard_list))
            par = link.getroot()
            # print((urlopen(forvard_list).read()).decode('utf-8'))
            # print(log)

            #print(par.find('ok'))
            if par.find('ok') != None:
                id_fw = []
                forward = []
                copy = []
                filter_params = []
                enabled_forw = []

                for elem in par.findall('ok/filters/filter'):
                    id_fw.append(elem.find('id').text)
                    forward.append(elem.find('forward').text)
                    copy.append(elem.find('copy').text)
                    filter_params.append(elem.find('filter_param').text)
                    enabled_forw.append(elem.find('enabled').text)

                    if not Forward.objects.filter(id_fw=elem.find('id').text):
                        f = Forward.objects.create(
                            info_email_id=InfoEmail.objects.get(login=log).id,
                            id_fw=elem.find('id').text,
                            forwards=elem.find('forward').text,
                            copies=elem.find('copy').text,
                            filter_param=elem.find('filter_param').text,
                            enabled_forw=elem.find('enabled').text
                        )
                        f.save()

    def verification_forvard(*args):
        print('verification_forward')
        param1 = []
        param2 = []
        forward_for_del = []

        forward_name = MailAdmin.objects.filter(user=1).get().default_email_forward
        for i in args:
            # print(args)
            for n in i:

                # Проверка на активность переадресации
                if 'no' in n['enabled_forw']:
                    for g in range(len(n['enabled_forw'])):
                        if n['enabled_forw'][g] == 'no':
                            if n['filter_param'][g] == forward_name:
                                # Удаляем не активную переадресацию
                                link = URL_API + URL_DEL_FORWARD % (token, n['logins'], n['id_fw'][g])
                                urlopen(link)

                                param2.append(n['logins'])

                # Проверка на дубли переадресации по дефолту

                if n['filter_param'].count(forward_name) > 1:
                    # print(n['filter_param'].count(forward_name))
                    for i in range(len(n['filter_param'])):
                        if forward_name == n['filter_param'][i]:
                            pass
                            # Удаляем переадресацию
                            link = URL_API + URL_DEL_FORWARD % (token, n['logins'], n['id_fw'][i])
                            urlopen(link)

                    if n['logins'] not in param2:
                        param2.append(n['logins'])


                if n['logins'] != forward_name.split('@')[0]: #Если почта не есть дефолтом для переадресации
                    if n['filter_param'] != []: #Если список переадресации не пуст
                        if forward_name in n['filter_param']: # Если дефолтная почта установлена тогда нахер все...
                            param1.append(n['logins'])
                        else:
                            if n['logins'] not in param2:
                                param2.append(n['logins'])

                            # if param2.count(n['logins']) > 1: # Если логин повтряеться в списке
                            #     param2.remove(n['logins']) # удаляем нахер чтоб не путался под глазами
                    else: # Если список переадресации пуст
                        param2.append(n['logins'])

        for v in ExcludeEmail.objects.filter(user_id=1).values('email_info'): # Вытаскиваем ID со списка исключений
            for p in param2: # Вытаскиваем логины со списка
                # Если логин со списка совпадает с логином в списке исключеий, удаляем нахер
                if p in InfoEmail.objects.filter(id=v['email_info']).get().login:
                    # print('==')
                    param2.remove(p) #

        for login_for_set_forward in param2:
            link = URL_API + URL_SET_FORVARD % (token, login_for_set_forward, forward_name, 'yes')
            urlopen(link)
        YandexUpdate.update_forward(param2) #update for DB

    def del_forw(request):
        Forward.objects.get(id_fw=request.POST.get('id_fw')).delete()
        print(request.POST.get('id_fw'))

def usr(request):
    return auth.get_user(request).id

def login(request):
    args = {}
    args['title'] = 'Авторизация'
    args['form'] = LoginForm()
    if auth.get_user(request).is_authenticated:
        return redirect('/emails/')
    else:
        if request.POST and ('pause', not request.session):
            form = LoginForm(request.POST)
            if form.is_valid:
                username = form.data['username']
                password = form.data['password']
                remember = ''
                for n in [i for i in form.data]:
                    if n == 'remember_me':
                        remember =form.data['remember_me']
                user = auth.authenticate(username=username, password=password)
                if user is not None and remember == '':
                    auth.login(request, user)
                    request.session.set_expiry(900)
                    request.session['pause'] = True
                    messages.success(request, "Поздравлаем %s, Вы успешно вошли (временная сесcия 15мин.)" % auth.get_user(request).username,
                                     extra_tags="alert-success")
                    return redirect('/emails/')
                elif user is not None and remember == 'on':
                    auth.login(request, user)
                    messages.success(request, "Поздравлаем %s, Вы успешно вошли (долгосрочная сесcия)" % auth.get_user(request).username,
                                     extra_tags="alert-success")
                    return redirect('/emails/')
                else:
                    messages.error(request, "Внимание! Не коректно введены данные", extra_tags="alert-danger")
                    return render(request, 'yandex/_login.html', args)
            else:
                return render(request, 'yandex/_login.html', args)
    #return redirect('/emails/')
    return render(request, 'yandex/_login.html', args)

def logout(request):
    auth.logout(request)
    return redirect('/')

def render_to_json(request):
    django_messages = []
    data = {}

    for message in messages.get_messages(request):
        django_messages.append({
            "level": message.level,
            "message": message.message,
            "extra_tags": message.tags,
        })


        data['success'] = message.tags
        data['messages'] = django_messages
    return HttpResponse(simplejson.dumps(data, ensure_ascii=False).encode('utf-8'), content_type='application/json')

def parser(request):
    user_u = usr(request)
    Forward.objects.all().delete()
    YandexUpdate.pars(request)
    return redirect('/')

def upds(request):
    args = {}
    test = []
    args.update(csrf(request))
    if auth.get_user(request).is_authenticated:
        args['username'] = auth.get_user(request).username
        args['domain'] = DOMAIN
        args['add_e_form'] = AddEmail()
        args['set_forward'] = SetForward()
        args['del_forward'] = DelForward()
        args['edit_user'] = EditUser()
        user_u = usr(request)
        args['last_update_db'] = MailAdmin.objects.get(user=user_u).last_update_db


        for i in InfoEmail.objects.filter(domain__user=user_u):
            test.append({
                'logins': i.login,
                'maillist': [m[i] for m in Maillist.objects.filter(infoemail=i.id).values('name') for i in m],
                'sex': str(i.sex),
                'birth_date': str(i.birth_date),
                'iname': str(i.iname),
                'uid': str(i.uid),
                'enableds': i.enabled,
                'fname': str(i.fname),
                'ready': str(i.ready),
                'hintq': str(i.hintq),
                'aliases': [a[i] for a in Alliases.objects.filter(info_email=i.id).values('name') for i in a],
                'domain': MailAdmin.objects.get(user=auth.get_user(request).id).name,

                'id_email':[f for f in Forward.objects.filter(info_email=i.id).values('filter_param', 'info_email_id', 'copies', 'id_fw', 'forwards', 'enabled_forw')],
                'id_fw': [f[i] for f in Forward.objects.filter(info_email=i.id).values('id_fw') for i in f],
                'forward':[f[i] for f in Forward.objects.filter(info_email=i.id).values('forwards') for i in f],
                'copy': [f[i] for f in Forward.objects.filter(info_email=i.id).values('copies') for i in f],
                'filter_param': [f[i] for f in Forward.objects.filter(info_email=i.id).values('filter_param') for i in f],
                'enabled_forw': [f[i] for f in Forward.objects.filter(info_email=i.id).values('enabled_forw') for i in f],
            })
    return HttpResponse(simplejson.dumps(test, ensure_ascii=False).encode('utf-8'), content_type='application/json')

def index(request):


    # if request.user.is_authenticated():
    #     print('Authent')
    t = time.clock()
    args = {}
    test=[]
    args.update(csrf(request))
    if auth.get_user(request).is_authenticated:
        args['username'] = auth.get_user(request).username
        args['domain'] = DOMAIN
        args['add_e_form'] = AddEmail()
        args['set_forward'] = SetForward()
        args['del_forward'] = DelForward()
        args['edit_user'] = EditUser()
        args['exclude_email'] = AddExcludEmail()
        user_u = usr(request)
        args['last_update_db'] = MailAdmin.objects.get(user=user_u).last_update_db

        for i in InfoEmail.objects.filter(domain__user=user_u).order_by('uid'):
            test.append({
                'logins': i.login,
                'maillist': [m[i] for m in Maillist.objects.filter(infoemail=i.id).values('name') for i in m],
                'sex': str(i.sex),
                'birth_date': str(i.birth_date),
                'iname': str(i.iname),
                'uid': str(i.uid),
                'enabled': i.enabled,
                'fname': str(i.fname),
                'ready': str(i.ready),
                'hintq': str(i.hintq),
                'aliases': [a[i] for a in Alliases.objects.filter(info_email=i.id).values('name') for i in a],
                'domain': MailAdmin.objects.get(user=auth.get_user(request).id).name,

                'id_email':[f for f in Forward.objects.filter(info_email=i.id).values('filter_param', 'info_email_id', 'copies', 'id_fw', 'forwards', 'enabled_forw')],
                'id_fw': [f[i] for f in Forward.objects.filter(info_email=i.id).values('id_fw') for i in f],
                'forward':[f[i] for f in Forward.objects.filter(info_email=i.id).values('forwards') for i in f],
                'copy': [f[i] for f in Forward.objects.filter(info_email=i.id).values('copies') for i in f],
                'filter_param': [f[i] for f in Forward.objects.filter(info_email=i.id).values('filter_param') for i in f],
                # 'enabled_forw': [f[i] for f in Forward.objects.filter(info_email=i.id).values('enabled_forw') for i in f],
            })

        args['accounts'] = test
    else:
        return redirect('/')
    return render(request, '../templates/yandex/index.html', args)

def set_forward(request):
    args={}
    k = []
    if request.user.is_authenticated():

        if request.POST:

            if request.POST.get('is_copy') == 'true':

                link = URL_API + URL_SET_FORVARD % (token, request.POST.get('login'), request.POST.get('email_forward'), 'yes')
                urlopen(link)

                YandexUpdate.update_forward(request.POST.get('login'))

                messages.success(request, "Переадресация добавлена для %s c сохранением копии" % request.POST.get('login'),
                                        extra_tags="alert-success")

                for i in InfoEmail.objects.filter(domain__user=usr(request), login=request.POST.get('login')):
                    k.append({
                        'logins': i.login,
                        'maillist': [m[i] for m in Maillist.objects.filter(infoemail=i.id).values('name') for i in m],
                        'sex': str(i.sex),
                        'birth_date': str(i.birth_date),
                        'iname': str(i.iname),
                        'uid': str(i.uid),
                        'enabled': i.enabled,
                        'fname': str(i.fname),
                        'ready': str(i.ready),
                        'hintq': str(i.hintq),
                        'aliases': [a[i] for a in Alliases.objects.filter(info_email=i.id).values('name') for i in a],
                        'domain': MailAdmin.objects.get(user=auth.get_user(request).id).name,

                        'id_email':[f for f in Forward.objects.filter(info_email=i.id).values('filter_param', 'info_email_id',
                                                                                              'copies', 'id_fw', 'forwards',
                                                                                              'enabled_forw')],
                    })

                return HttpResponse(simplejson.dumps(k, ensure_ascii=False).encode('utf-8'), content_type='application/json')
            else:
                link = URL_API + URL_SET_FORVARD % (token, request.POST.get('login'), request.POST.get('email_forward'), 'no')
                urlopen(link)

                YandexUpdate.update_forward(request.POST.get('login'))

                for i in InfoEmail.objects.filter(domain__user=usr(request), login=request.POST.get('login')):
                    k.append({
                        'logins': i.login,
                        'maillist': [m[i] for m in Maillist.objects.filter(infoemail=i.id).values('name') for i in m],
                        'sex': str(i.sex),
                        'birth_date': str(i.birth_date),
                        'iname': str(i.iname),
                        'uid': str(i.uid),
                        'enabled': i.enabled,
                        'fname': str(i.fname),
                        'ready': str(i.ready),
                        'hintq': str(i.hintq),
                        'aliases': [a[i] for a in Alliases.objects.filter(info_email=i.id).values('name') for i in a],
                        'domain': MailAdmin.objects.get(user=auth.get_user(request).id).name,

                        'id_email': [f for f in
                                     Forward.objects.filter(info_email=i.id).values('filter_param', 'info_email_id',
                                                                                    'copies', 'id_fw',
                                                                                    'forwards', 'enabled_forw')],
                    })
                    # print(k)

                    messages.success(request, "Переадресация добавлена для %s без сохранением копии" % request.POST.get('login'),
                                     extra_tags="alert-success")
                    # print(messages)
            return HttpResponse(simplejson.dumps(k, ensure_ascii=False).encode('utf-8'), content_type='application/json')

def reg_user_token(request):
    k = []
    # if request.POST:
    #     form = AddEmail(request.POST)
    #
    #     if form.is_valid():
    #         login = form.data['login']
    #         if form.data['passw1'] == form.data['passw2']:
    #             passw = form.data['passw1']
    #             regist = URL_API + URL_REG_USER_token % (token, login, passw)
    #             link = ET.parse(urlopen(regist))
    #             par = link.getroot()
    #
    #             YandexUpdate.get_user_info(form.data['login'])
    #
    #             for n in [i for i in form.data]:
    #                 if n == 'is_forward':
    #                     if par.find('ok') != None:
    #
    #                         messages.success(request, "Электронный ящик создан %s" % form.data['login'] + '@' + DOMAIN,
    #                                          extra_tags="alert-success")
    #
    #                         return redirect('/emails/')
    #                     else:
    #                         if par.find('error').attrib['reason'] == 'occupied':
    #                             messages.error(request, "Такой логин уже занят", extra_tags="alert-warning")
    #                             return redirect('/emails/')
    #                         elif par.find('error').attrib['reason'] == 'passwd-tooshort':
    #                             messages.error(request, "Пароль слишком короткий. 6 и больше символов допустимо",
    #                                            extra_tags="alert-warning")
    #                             return redirect('/emails/')
    #                         elif par.find('error').attrib['reason'] == 'passwd-badpasswd':
    #                             messages.error(request, "Пароль слишком прост", extra_tags="alert-warning")
    #                             return redirect('/emails/')
    #
    #             set_forward(request, form.data['login'])
    #             messages.success(request, "Электронный ящик создан %s" % form.data['login'] + '@' + DOMAIN,
    #                              extra_tags="alert-success")
    #             return redirect('/emails/')
    #         else:
    #             messages.error(request, "Пароли не совпадают", extra_tags="alert-warning")
    #             return redirect('/emails/')
    # return redirect('/emails/')
    if request.user.is_authenticated():
        if request.POST:
            if request.POST.get('password1') == request.POST.get('password2'):
                regist = URL_API + URL_REG_USER_token % (token, request.POST.get('login'), request.POST.get('password1'))
                link = ET.parse(urlopen(regist))
                par = link.getroot()

                em = InfoEmail.objects.create(
                    login=request.POST.get('login'),
                    domain_id=MailAdmin.objects.get(user_id = 1).id,
                    sex='no update DB',
                    birth_date='no update DB',
                    iname='no update DB',
                    fname='no update DB',
                    uid='no update DB',
                    enabled='yes',
                    ready='no update DB',
                )
                em.save()

                if request.POST.get('is_forward') == 'true':
                    # Parser for forward
                    id_fw = []
                    forward = []
                    copy = []
                    filter_params = []

                    forvard_list = URL_API + URL_GET_FORVARD_LIST % (token, request.POST.get('login'))
                    link = ET.parse(urlopen(forvard_list))

                    pars = link.getroot()

                    for elem in pars.findall('ok/filters/filter'):
                        id_fw.append(elem.find('id').text)
                        forward.append(elem.find('forward').text)
                        copy.append(elem.find('copy').text)
                        filter_params.append(elem.find('filter_param').text)

                        if not Forward.objects.filter(id_fw=elem.find('id').text):
                            f = Forward.objects.create(
                                info_email_id=em.id,
                                id_fw=elem.find('id').text,
                                forward=elem.find('forward').text,
                                copy=elem.find('copy').text,
                                filter_param=elem.find('filter_param').text
                            )
                            f.save()
                for i in InfoEmail.objects.filter(domain__user=usr(request), login=request.POST.get('login')):
                    k.append({
                        'logins': i.login,
                        'maillist': [m[i] for m in Maillist.objects.filter(infoemail=i.id).values('name') for i
                                     in m],
                        'sex': str(i.sex),
                        'birth_date': str(i.birth_date),
                        'iname': str(i.iname),
                        'uid': str(i.uid),
                        'enabled': i.enabled,
                        'fname': str(i.fname),
                        'ready': str(i.ready),
                        'hintq': str(i.hintq),
                        'aliases': [a[i] for a in Alliases.objects.filter(info_email=i.id).values('name') for i
                                    in a],
                        'domain': MailAdmin.objects.get(user=auth.get_user(request).id).name,

                        'id_email': [f for f in Forward.objects.filter(info_email=i.id).values('filter_param',
                                                                                               'info_email_id',
                                                                                               'copies',
                                                                                               'id_fw',
                                                                                               'forwards')],
                    })

                if par.find('ok') != None:
                    print('if')

                    messages.success(request, "Электронный ящик создан %s" % request.POST.get('login') + '@' + DOMAIN,
                                    extra_tags="alert-success")

                    return HttpResponse(simplejson.dumps(k, ensure_ascii=False).encode('utf-8'),
                                    content_type='application/json')

                else:
                    if par.find('error').attrib['reason'] == 'occupied':
                        messages.error(request, "Такой логин уже занят", extra_tags="alert-warning")
                        return HttpResponse(simplejson.dumps(k, ensure_ascii=False).encode('utf-8'),
                                                content_type='application/json')
                    elif par.find('error').attrib['reason'] == 'passwd-tooshort':
                        messages.error(request, "Пароль слишком короткий. Допустимо 6 и больше символов",
                                       extra_tags="alert-warning")
                        return HttpResponse(simplejson.dumps(k, ensure_ascii=False).encode('utf-8'),
                                            content_type='application/json')
                    elif par.find('error').attrib['reason'] == 'passwd-badpasswd':
                        messages.error(request, "Пароль слишком прост. Должен содержать от 6 до 20 символов — латинские буквы, цифры или спецсимволы (допускаются знаки ` ! @ # $ % ^ & * ( ) - _ = + [ ] { } ; : \" \ | , . < > / ?, не допускаются ~ и ')", extra_tags="alert-warning")
                        return HttpResponse(simplejson.dumps(k, ensure_ascii=False).encode('utf-8'),
                                            content_type='application/json')
            else:
                messages.error(request, "Пароли не совпадают", extra_tags="alert-warning")

        return HttpResponse(simplejson.dumps(k, ensure_ascii=False).encode('utf-8'), content_type='application/json')

def delete_user(request):
    k=[]
    if auth.get_user(request).username:
        if request.POST:
            urls = URL_API + URL_DEL_USER % (token, request.POST.get('login'))
            link = ET.parse(urlopen(urls))
            par = link.getroot()

            if par.find('ok') != None:
                messages.success(request, "Электронный ящик %s удален" % request.POST.get('login'), extra_tags="alert-success")
                InfoEmail.objects.get(login=request.POST.get('login')).delete()
                return HttpResponse(simplejson.dumps(k, ensure_ascii=False).encode('utf-8'),
                                    content_type='application/json')
            else:
                messages.error(request, "Не удалось удалить %s" % request.POST.get('login'), extra_tags="alert-warning")
                return HttpResponse(simplejson.dumps(k, ensure_ascii=False).encode('utf-8'),
                                    content_type='application/json')

def edit_user(request):
    k=[]
    if request.POST:
        login = request.POST.get('login_edit')
        password = request.POST.get('password')
        domain_name = request.POST.get('domain_name')
        iname = request.POST.get('iname')
        fname = request.POST.get('fname')
        sex = request.POST.get('sex')
        hintq = request.POST.get('hintq')
        hinta = request.POST.get('hinta')
        link = URL_API+URL_EDIT_USER % (token, login, password, domain_name, iname, fname, sex, quote(hintq), quote(hinta))
        pr = ET.parse(urlopen(link))
        par = pr.getroot()
        if par.find('ok') != None:
            messages.success(request, "Внесены изменения для %s" % request.POST.get('login_edit') + '@' + DOMAIN,
                             extra_tags="alert-success")
            InfoEmail.objects.filter(login=login).update(iname = iname, fname = fname, sex = sex, hintq = hintq)

    return redirect('/emails/')

def del_forward(request, login, id_fw):
    if auth.get_user(request).username:
        link = URL_API + URL_DEL_FORWARD % (token, login, id_fw)
        urlopen(link)
        messages.success(request, "Для ящика %s  переадресация была удалена " % login, extra_tags="alert-success")
        Forward.objects.get(id_fw=id_fw).delete()
        return redirect('/emails/')
    else:
        messages.error(request, "Вы не авторизированы",
                         extra_tags="alert-warning")
        return redirect('/')

def del_forw(request):
    test = []
    # print(request.POST)
    if auth.get_user(request).username:
        if request.POST:
            link = URL_API + URL_DEL_FORWARD % (token, request.POST.get('login'), request.POST.get('id_fw'))
            urlopen(link)
            messages.success(request, "Для ящика %s  переадресация была удалена " % request.POST.get('login'), extra_tags="alert-success")

            Forward.objects.get(id_fw=request.POST.get('id_fw')).delete()

            forvard_list = URL_API + URL_GET_FORVARD_LIST % (token, request.POST.get('login'))
            link = ET.parse(urlopen(forvard_list))
            par = link.getroot()
            if par.find('ok') != None:
                for elem in par.findall('ok/filters/filter'):
                    test.append({
                        'id_fw':elem.find('id').text,
                        'forwards':elem.find('forward').text,
                        'copyes':elem.find('copy').text,
                        'filter_params':elem.find('filter_param').text
                    })

            return HttpResponse(simplejson.dumps(test, ensure_ascii=False).encode('utf-8'),
                                content_type='application/json')
        else:
            messages.error(request, "Вы не авторизированы",
                             extra_tags="alert-warning")

    return HttpResponse(simplejson.dumps(test, ensure_ascii=False).encode('utf-8'), content_type='application/json')

