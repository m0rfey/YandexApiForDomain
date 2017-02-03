#from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.db import models

#
#8ce7284484b2474857d17335c2acd0d2c4cc6203aaa4b743b1656bf3

# TEST TOKEN
# Registrar name: m0rfey
# Registrar id 4327985
# PAI6YYAHZ4WCIOCYPCWHJOXXTYALNBQS3DKEKLXQU7OENXGYA3OQ

# OAuth client ID
# d68fa7812f44463486ff49385bc2a6a8

# Domain Token photomax.pp.ua for ADMIN
# MPH4VCRK3URFYQLW3YBELJ7UDCLL6T6L36T5EN5JITGI6JDCYZWA
# 8ce7284484b2474857d17335c2acd0d2c4cc6203aaa4b743b1656bf3

# Oauth get-oauth-token-docpage
# AQAAAAAUUzXiAAPuKOUpVUxovEsAk5L2_4oalXc
# AQAAAAAUUzXiAAPuKHBptWq6HU9Kv3PqFLRq3ss

class MailAdmin(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(verbose_name='Домен', max_length=100, unique=True)
    token1 = models.CharField(verbose_name='API_v1 Token', max_length=250)
    token2 = models.CharField(verbose_name='API_v2 Token', max_length=250)
    last_update_db = models.DateTimeField(verbose_name='Last update Data Base')

    default_email_forward = models.EmailField(max_length=50, blank=True, null=True, verbose_name='Почта для переадресации')

    class Meta:
        verbose_name = 'Настройки'
        verbose_name_plural = 'Настройки'

    def __str__(self):
        return self.name


class InfoEmail(models.Model):
    login = models.CharField(max_length=50)
    domain = models.ForeignKey(MailAdmin, related_name='MailAdmin')
    sex = models.CharField(blank=True, null=True, max_length=50)
    birth_date = models.CharField(blank=True, null=True, max_length=50)
    iname = models.CharField(blank=True, null=True, max_length=50)
    fname = models.CharField(blank=True, null=True, max_length=50)
    uid = models.CharField(blank=True, null=True, max_length=50)
    enabled = models.CharField(blank=True, null=True, max_length=50)
    ready = models.CharField(blank=True, null=True, max_length=50)
    hintq = models.CharField(verbose_name='Secret Question', max_length=50, blank=True, null=True,)


    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'

    def __str__(self):
        return self.login


class Alliases(models.Model):
    name = models.CharField(blank=True, null=True, max_length=50)
    info_email = models.ForeignKey(InfoEmail)

    class Meta:
        verbose_name = 'Алиас'
        verbose_name_plural = 'Алиас'

class Maillist(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True,)
    infoemail = models.ForeignKey(InfoEmail)

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

class Forward(models.Model):
    info_email = models.ForeignKey(InfoEmail, blank=True, null=True, max_length=50)
    id_fw = models.CharField(verbose_name='Forward ID', blank=True, null=True, max_length=50)
    forwards = models.CharField(verbose_name='Forward (Yes/No)', blank=True, null=True, max_length=50)
    copies = models.CharField(verbose_name='Copy (Yes/No)', blank=True, null=True, max_length=50)
    filter_param = models.CharField(verbose_name='Forwarding to', blank=True, null=True, max_length=50)
    enabled_forw = models.CharField(verbose_name='Enabled (Yes/No)', blank=True, null=True, max_length=10)

    class Meta:
        verbose_name = 'Переадресация'
        verbose_name_plural = 'Переадресации'

    def __str__(self):
        lst=({'info_e':self.info_email_id, 'id_fw':self.id_fw, 'forward':self.forwards, 'copy':self.copies, 'filter_param':self.filter_param})
        return str(self.info_email)

class ExcludeEmail(models.Model):
    user =  models.ForeignKey(User)
    email_info = models.ManyToManyField(InfoEmail)

    class Meta:
        verbose_name = 'Список исключений'
        verbose_name_plural = 'Список исключений'
