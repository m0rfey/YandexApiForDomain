from django.contrib import admin
from .models import MailAdmin, InfoEmail, Alliases, Maillist, Forward, ExcludeEmail


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
    list_display = ['info_email', 'id_fw', 'forwards', 'copies', 'filter_param']
    raw_id_fields = ['info_email']
    # list_editable = ['id_fw', 'forwards', 'copies', 'filter_param']
    search_fields =['info_email']

class ExcludeEmailAdmin(admin.ModelAdmin):
    filter_horizontal = ['email_info']
    list_display = ['user', 'id']

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    class Meta:
        model = ExcludeEmail

admin.site.register(MailAdmin, MailAdminAdmin)
admin.site.register(InfoEmail, InfoEmailAdmin)
admin.site.register(Alliases, AlliasesAdmin)
admin.site.register(Maillist, MaillistAdmin)
admin.site.register(Forward, ForwardAdmin)
admin.site.register(ExcludeEmail, ExcludeEmailAdmin)
