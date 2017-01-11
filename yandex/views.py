#-*- coding: utf-8 -*-

import datetime
import json
import http.client

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib import auth
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.context_processors import csrf

from yandex.api_yandex import *
from .models import InfoEmail, Alliases, Maillist, Forward
from .forms import AddEmail, SetForward, DelForward, LoginForm, EditUser
from urllib.request import urlopen, Request
import xml.etree.ElementTree as ET
import time
from django.views.decorators.csrf import csrf_protect


class YandexUpdate(object):

    _request = {}

    def check_user(self):
        check_us = URL_API + URL_CHECK_USER (token, self)

    def get_user_info(self):
        user_info = URL_API + URL_GET_USER_INFO %(token, self)
        link = ET.parse(urlopen(user_info))
        par = link.getroot()
        if par.find('ok') != None:
            for elem in par.findall('ok/filters/filter'):
                print(elem)


    def pars(self):
        print('Run pars')
        args = {}

        list_email = URL_API + URL_GET_LIST
        loads = (urlopen(list_email).read()).decode('utf-8')
        j = json.loads(str(loads))

        test = []
        page = 1
        if j['pages'] >= 1:  # Если страниц больше 1
            for i in range(1, j['pages'] + 1):
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

                        for elem in par.findall('ok/filters/filter'):
                            id_fw.append(elem.find('id').text)
                            forward.append(elem.find('forward').text)
                            copy.append(elem.find('copy').text)
                            filter_param.append(elem.find('filter_param').text)
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
                        })
        args['accounts'] = test
        domain = MailAdmin.objects.get(user_id__gte = 1).id
        YandexUpdate.verification_forvard(args['accounts'])
        YandexUpdate.save(domain, test)
        MailAdmin.objects.filter(user = 1).update(last_update_db=datetime.datetime.now())

    def save(domain, *args):
        InfoEmail.objects.all().delete()
        print('Save')
        for account in args:
            for ac in account:
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
                                    forward=elem.find('forward').text,
                                    copy=elem.find('copy').text,
                                    filter_param=elem.find('filter_param').text
                                )
                                f.save()

                else:
                    pass


    def update_forward(log):
        print('update_forward')
        forvard_list = URL_API+ URL_GET_FORVARD_LIST % (token, log)
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
                        info_email_id=InfoEmail.objects.get(login=log).id,
                        id_fw=elem.find('id').text,
                        forward=elem.find('forward').text,
                        copy=elem.find('copy').text,
                        filter_param=elem.find('filter_param').text
                    )
                    f.save()

    def verification_forvard(*args):
        print('verification_forvard')
        if MailAdmin.objects.filter(user=1).get().default_email_forward != None:
            forward_name = MailAdmin.objects.filter(user=1).get().default_email_forward
            for i in args:
                for n in i:
                    if n['logins'] != forward_name.split('@')[0]:
                        if n['forward'] == []:
                            link = URL_API + URL_SET_FORVARD % (token, n['logins'], forward_name, 'yes')
                            urlopen(link)
                            YandexUpdate.update_forward(n['logins'])


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
                    request.session.set_expiry(15000)
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

# def verifications(request):
#     accounts = request
#     forward_name = MailAdmin.objects.filter(user=1).get().default_email_forward
#     for i in accounts:
#         if i['logins'] != forward_name.split('@')[0]:
#             if i['forward'] ==[]:
#                 link = URL_API + URL_SET_FORVARD % (token, i['logins'], forward_name, 'yes')
#                 urlopen(link)
#                 YandexUpdate.update_forward(i['logins'])
#
#     return redirect('/')

def parser(request):
    # args = {}
    #
    # list_email = URL_API + URL_GET_LIST
    # loads = (urlopen(list_email).read()).decode('utf-8')
    # j = json.loads(str(loads))
    #
    # test = []
    # page = 1
    # if j['pages'] >= 1:  # Если страниц больше 1
    #     for i in range(1, j['pages'] + 1):
    #         page = i
    #         list_email = URL_API + URL_GET_LIST_PAGE % (TOKEN, DOMAIN, page)
    #         loads = (urlopen(list_email).read()).decode('utf-8')
    #         j = json.loads(str(loads))
    #         for account in j['accounts']:
    #             forvard_list = URL_API + URL_GET_FORVARD_LIST % (token, account['login'])
    #             # urls = urlopen(forvard_list)
    #
    #             link = ET.parse(urlopen(forvard_list))
    #             par = link.getroot()
    #
    #             if par.find('ok') != None:
    #                 id_fw = []
    #                 forward = []
    #                 copy = []
    #                 filter_param = []
    #                 t = {}
    #
    #                 for elem in par.findall('ok/filters/filter'):
    #                     id_fw.append(elem.find('id').text)
    #                     forward.append(elem.find('forward').text)
    #                     copy.append(elem.find('copy').text)
    #                     filter_param.append(elem.find('filter_param').text)
    #                 test.append({
    #                     'logins': account['login'].split('@')[0],
    #                     'domain': j['domain'],
    #                     'maillist': account['maillist'],
    #                     'sex': str(account['sex']),
    #                     'birth_date': str(account['birth_date']),
    #                     'iname': str(account['iname']),
    #                     'uid': str(account['uid']),
    #                     'enabled': account['enabled'],
    #                     'fname': str(account['fname']),
    #                     'ready': str(account['ready']),
    #                     'aliases': account['aliases'],
    #                     'hintq': account['hintq'],
    #
    #                     'id_fw': id_fw,
    #                     'forward': forward,
    #                     'copy': copy,
    #                     'filter_param': filter_param,
    #                 })
    #             else:
    #                 test.append({
    #                     'logins': account['login'].split('@')[0],
    #                     'maillist': account['maillist'],
    #                     'sex': str(account['sex']),
    #                     'birth_date': str(account['birth_date']),
    #                     'iname': str(account['iname']),
    #                     'uid': str(account['uid']),
    #                     'enabled': account['enabled'],
    #                     'fname': str(account['fname']),
    #                     'ready': str(account['ready']),
    #                     'aliases': account['aliases'],
    #
    #                     'id_fw': None,
    #                     'forward': None,
    #                     'copy': None,
    #                     'filter_param': None,
    #                 })
    # InfoEmail.objects.all().delete()
    # dom = MailAdmin.objects.get(user_id__gte=auth.get_user(request).id).id
    # args['accounts'] = test
    # YandexUpdate.verification_forvard(args['accounts'])
    # #verifications(args['accounts'])
    # yup = YandexUpdate
    # yup.save(dom, args['accounts'])
    # MailAdmin.objects.filter(user=auth.get_user(request).id).update(last_update_db=datetime.datetime.now())
    
    YandexUpdate.pars(request)
    return redirect('/')

def index(request):
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
        args['last_update_db'] = MailAdmin.objects.get(user=auth.get_user(request).id).last_update_db

        for i in InfoEmail.objects.filter(domain__user=auth.get_user(request).id):
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

                'id_fw': [f[i] for f in Forward.objects.filter(info_email=i.id).values('id_fw') for i in f],
                'forward':[f[i] for f in Forward.objects.filter(info_email=i.id).values('forward') for i in f],
                'copy': [f[i] for f in Forward.objects.filter(info_email=i.id).values('copy') for i in f],
                'filter_param': [f[i] for f in Forward.objects.filter(info_email=i.id).values('filter_param') for i in f],
            })

        args['accounts'] = test
    else:
        return redirect('/')
    return render(request, '../templates/yandex/index.html', args)


@csrf_protect
def get_detail(request):
    args={}
    if request.POST:
        login = request.POST['login']
        forward_name = request.POST['forward_name']
        link = URL_API+URL_SET_FORVARD % (token, login, forward_name, 'yes')
        urlopen(link)
        return request('/')
    return request('/')

def set_forward(request, login):
    if request.POST:
        form = SetForward(request.POST)
        if form.is_valid():
            for n in [i for i in form.data]:
                if n == 'is_copy':
                    link = URL_API + URL_SET_FORVARD % (token, login, form.data['email_forward'], 'yes')
                    urlopen(link)
                    messages.success(request, "Переадресация добавлена для %s c сохранением копии" % login,
                                     extra_tags="alert-success")
                    YandexUpdate.update_forward(login)
                    return redirect('/')

            link = URL_API + URL_SET_FORVARD % (token, login, form.data['email_forward'], 'no')
            urlopen(link)
            messages.success(request, "Переадресация добавлена для %s без сохранением копии" % login,
                             extra_tags="alert-success")
            YandexUpdate.update_forward(login)
            return redirect('/')
    return redirect('/')

def reg_user_token(request):
    if request.POST:
        form = AddEmail(request.POST)

        if form.is_valid():
            login = form.data['login']
            if form.data['passw1'] == form.data['passw2']:
                passw = form.data['passw1']
                regist = URL_API + URL_REG_USER_token % (token, login, passw)
                link = ET.parse(urlopen(regist))
                par = link.getroot()

                YandexUpdate.get_user_info(form.data['login'])

                for n in [i for i in form.data]:
                    if n == 'is_forward':
                        if par.find('ok') != None:

                            messages.success(request, "Электронный ящик создан %s" % form.data['login']+'@'+DOMAIN, extra_tags="alert-success")

                            return redirect('/emails/')
                        else:
                            if par.find('error').attrib['reason'] == 'occupied':
                                messages.error(request, "Такой логин уже занят", extra_tags="alert-warning")
                                return redirect('/emails/')
                            elif par.find('error').attrib['reason'] == 'passwd-tooshort':
                                messages.error(request, "Пароль слишком короткий. 6 и больше символов допустимо", extra_tags="alert-warning")
                                return redirect('/emails/')
                            elif par.find('error').attrib['reason'] == 'passwd-badpasswd':
                                messages.error(request, "Пароль слишком прост", extra_tags="alert-warning")
                                return redirect('/emails/')

                set_forward(request, form.data['login'])
                messages.success(request, "Электронный ящик создан %s" % form.data['login'] + '@' + DOMAIN,
                                    extra_tags="alert-success")
                return redirect('/emails/')
            else:
                messages.error(request, "Пароли не совпадают", extra_tags="alert-warning")
                return redirect('/emails/')
    return redirect('/emails/')

def delete_user(request, login):
    t = time.clock()
    urls = URL_API + URL_DEL_USER % (token, login.split('@')[0])
    link = ET.parse(urlopen(urls))
    par = link.getroot()

    if par.find('ok') != None:
        InfoEmail.objects.get(login=login).delete()
        messages.success(request, "Электронный ящик %s удален" % login, extra_tags="alert-success")
        return redirect('/emails/')
    else:
        messages.error(request, "Не удалось удалить %s" % login, extra_tags="alert-warning")
        return redirect('/emails/')

def edit_user(request):
    if request.POST:
        form = EditUser(request.POST)
        if form.is_valid:
            login = form.data['login_edit'].encode('utf-8')
            password = form.data['password'].encode('utf-8')
            domain_name = form.data['domain_name'].encode('utf-8')
            iname = form.data['iname'].encode('utf-8')
            fname = form.data['fname'].encode('utf-8')
            sex = form.data['sex'].encode('utf-8')
            hintq = form.data['hintq'].encode('utf-8')
            hinta = form.data['hinta'].encode('utf-8')

            link = URL_API+URL_EDIT_USER % (token, login, password, domain_name, iname, fname, sex, hintq, hinta)
            urlopen(link)
            #dm = MailAdmin.objects.get(name=domain_name).id
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


# Create your views here.
