# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User

from .api_yandex import DOMAIN
from .models import MailAdmin


class AddEmail(forms.Form):
    login = forms.CharField(
        label='@'+DOMAIN,
        widget=forms.TextInput({'class': 'form-control', 'placeholder': 'Логин', 'aria-describedby':'basic-addon2'})
    )
    passw1 = forms.CharField(
        label='',
        widget=forms.PasswordInput({'class': 'form-control', 'placeholder' : 'Пароль'}),
    )
    passw2 = forms.CharField(
        label='',
        widget=forms.PasswordInput({'class': 'form-control','placeholder': 'Повторите пароль'}),
    )
    is_forward = forms.BooleanField(
        label='Добавить пересылку',
        required=False,
        widget=forms.CheckboxInput({ 'onclick': 'return CheckForward(window.event)'}),
    )
    field = ['login', 'passw1', 'passw2', 'is_forward']

class SetForward(forms.Form):
    email_forward = forms.CharField(
        label='',
        widget=forms.EmailInput({'class': 'form-control', 'placeholder': 'Email для переадресации'}),
    )
    is_copy = forms.BooleanField(
        label='Оставлять копию',
        required=False,
        widget=forms.CheckboxInput({'class': 'checkbox'}),
    )

    field = ['email_forward', 'is_copy']

class DelForward(forms.Form):
    em = forms.ModelChoiceField(
        label='Выберете что удалить',
        queryset=MailAdmin.objects.none(),
        widget=forms.Select({'class': 'form-control'}),
    )
    field = ['em']

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        label='',
        widget=forms.TextInput({'class': 'form-control','placeholder': 'Логин'})
    )
    password = forms.CharField(
        max_length=50,
        label='',
        widget=forms.PasswordInput({'class': 'form-control','placeholder': 'Пароль'})
    )
    remember_me = forms.BooleanField(
        label='Остаться на сайте',
        required=False,
        widget=forms.CheckboxInput({'class': 'checkbox'}),
    )

    def clean(self):
        try:
            mail_user = User.objects.active().select_related().get(internal_username=self.cleaned_data['username'])
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            raise forms.ValidationError("Incorrect username or password")

        if self.cleaned_data.get('password') and mail_user.authenticate(self.cleaned_data['password']):
            self.cleaned_data['user'] = mail_user
        else:
            raise forms.ValidationError("Incorrect username or password")

        return self.cleaned_data

class EditUser(forms.Form):
    CHOICES = [
        ('0',' -Пол- '),
        ('1','муж.'),
        ('2','жен.')]

    login_edit = forms.CharField(
        label='',
        widget=forms.TextInput({'class':'form-control','placeholder': 'Логин'})
    )
    password = forms.CharField(
        label='',
        widget=forms.TextInput({'class':'form-control','placeholder': 'Пароль'})
    )
    domain_name = forms.CharField(
        label='',
        widget=forms.TextInput({'class':'form-control','placeholder': 'Домен'})
    )
    iname = forms.CharField(
        label='',
        widget=forms.TextInput({'class':'form-control','placeholder': 'Имя'})
    )
    fname = forms.CharField(
        label='',
        widget=forms.TextInput({'class':'form-control','placeholder': 'Фамилия'})
    )
    sex = forms.ChoiceField(
        label='',
        choices=CHOICES,
        widget=forms.Select({'class':'form-control','placeholder': 'Пол', 'selected':'0'})
    )
    hintq = forms.CharField(
        label='',
        widget=forms.TextInput({'class':'form-control','placeholder': 'Секретный вопрос'})
    )
    hinta = forms.CharField(
        label='',
        widget=forms.TextInput({'class':'form-control','placeholder': 'Ответ на секретный вопрос'})
    )
