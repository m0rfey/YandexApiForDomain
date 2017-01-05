from django.contrib import admin
from .models import MailAdmin, InfoEmail, Alliases, Maillist, Forward


class MailAdminAdmin(admin.ModelAdmin):
    class Meta:
        model = MailAdmin
        # fields = ['name', 'token']

class InfoEmailAdmin(admin.ModelAdmin):
    class Meta:
        model = InfoEmail

class AlliasesAdmin(admin.ModelAdmin):
    class Meta:
        model = Alliases

class MaillistAdmin(admin.ModelAdmin):
    class Meta:
        model = Maillist

class ForwardAdmin(admin.ModelAdmin):
    class Meta:
        model = Forward

admin.site.register(MailAdmin, MailAdminAdmin)
admin.site.register(InfoEmail, InfoEmailAdmin)
admin.site.register(Alliases, AlliasesAdmin)
admin.site.register(Maillist, MaillistAdmin)
admin.site.register(Forward, ForwardAdmin)
