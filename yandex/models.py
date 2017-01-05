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

    default_email_forward = models.EmailField(max_length=50, blank=True, null=True, verbose_name='Почта для переадресации')

    class Meta:
        verbose_name = 'Mail Admin'
        verbose_name_plural = 'Mail Admin'

    def __str__(self):
        return self.name


class InfoEmail(models.Model):
    login = models.CharField(max_length=50)
    domain = models.ForeignKey(MailAdmin)
    sex = models.CharField(blank=True, null=True, max_length=50)
    birth_date = models.CharField(blank=True, null=True, max_length=50)
    iname = models.CharField(blank=True, null=True, max_length=50)
    fname = models.CharField(blank=True, null=True, max_length=50)
    uid = models.CharField(max_length=50)
    enabled = models.CharField(blank=True, null=True, max_length=50)
    ready = models.CharField(blank=True, null=True, max_length=50)
    hintq = models.CharField(verbose_name='Secret Question', max_length=50)

    class Meta:
        verbose_name = 'Info Email'
        verbose_name_plural = 'Info Email'


class Alliases(models.Model):
    name = models.CharField(blank=True, null=True, max_length=50)
    info_email = models.ForeignKey(InfoEmail)

    class Meta:
        verbose_name = 'Alliases'
        verbose_name_plural = 'Alliases'

class Maillist(models.Model):
    name = models.CharField(max_length=50)
    infoemail = models.ForeignKey(InfoEmail)

    class Meta:
        verbose_name = 'Maillist'
        verbose_name_plural = 'Maillist'

class Forward(models.Model):
    info_email = models.CharField(blank=True, null=True, max_length=50)
    id_fw = models.CharField(blank=True, null=True, max_length=50)
    forward = models.CharField(verbose_name='Yes/No', blank=True, null=True, max_length=50)
    copy = models.CharField(verbose_name='Yes/No', blank=True, null=True, max_length=50)
    filter_param = models.CharField(verbose_name='Forwarding to', blank=True, null=True, max_length=50)

    class Meta:
        verbose_name = 'Forward'
        verbose_name_plural = 'Forward'
