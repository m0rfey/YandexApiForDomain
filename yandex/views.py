#-*- coding: utf-8 -*-

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

def update_bd(request):
    dm = MailAdmin.objects.filter(user=auth.get_user(request).id).values('name')
    for i in dm:
        inf_email = InfoEmail.objects.filter(domain__name=i['name'])
        print(inf_email)
        allias = Alliases.objects.filter(info_email=inf_email)
        maillist = Maillist.objects.filter(infoemail=inf_email)
        forward = Forward.objects.filter(info_email=inf_email)


def paginators(request):
    t = time.clock()
    accounts = request
    forward_name = 'm0rfey@photomax.pp.ua'
    for i in accounts:
        if i['logins'] != forward_name.split('@')[0]:
            if i['forward'] ==[]:
                link = URL_API + URL_SET_FORVARD % (token, i['logins'], forward_name, 'yes')
                urlopen(link)
    print('pagin', time.clock()-t)

    return redirect('/')


def index(request):
    t = time.clock()
    args = {}
    args.update(csrf(request))
    if auth.get_user(request).is_authenticated:
        args['username'] = auth.get_user(request).username
        args['domain'] = DOMAIN
        args['add_e_form'] = AddEmail()
        args['set_forward'] = SetForward()
        args['del_forward'] = DelForward()
        args['edit_user'] = EditUser()
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
                    #urls = urlopen(forvard_list)

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
    else:
        return redirect('/')
    args['accounts'] = test
    end_t = time.clock() - t
    print('index', end_t)
    paginators(args['accounts'])
    update_bd(request)

    return render(request, '../templates/yandex/index.html', args)


@csrf_protect
def get_detail(request):
    args={}
    if request.POST:
        print(request.POST['login'], request.POST['forward_name'])
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
                    return redirect('/')

            link = URL_API + URL_SET_FORVARD % (token, login, form.data['email_forward'], 'no')
            urlopen(link)
            messages.success(request, "Переадресация добавлена для %s без сохранением копии" % login,
                             extra_tags="alert-success")
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
        messages.success(request, "Электронный ящик %s удален" % login, extra_tags="alert-success")
        print('delete_user',time.clock() - t)
        return redirect('/emails/')

    else:
        messages.error(request, "Не удалось удалить %s" % login, extra_tags="alert-warning")
        print(time.clock() - t)
        return redirect('/emails/')

def edit_user(request):
    if request.POST:
        form = EditUser(request.POST)
        if form.is_valid:
            login = form.data['login_edit']
            password = form.data['password']
            domain_name = form.data['domain_name']
            iname = form.data['iname']
            fname = form.data['fname']
            sex = form.data['sex']
            hintq = form.data['hintq']
            hinta = form.data['hinta']
            print(login)
            link = URL_API+URL_EDIT_USER % (token, login, password, domain_name, iname, fname, sex, hintq, hinta)
            urlopen(link)
        return redirect('/emails/')

def del_forward(request, login, id_fw):
    if auth.get_user(request).username:
        link = URL_API + URL_DEL_FORWARD % (token, login, id_fw)
        urlopen(link)
        messages.success(request, "Для ящика %s  переадресация была удалена " % login, extra_tags="alert-success")
        return redirect('/emails/')
    else:
        messages.error(request, "Вы не авторизированы",
                         extra_tags="alert-warning")
        return redirect('/')


# Create your views here.
