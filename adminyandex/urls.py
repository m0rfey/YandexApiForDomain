"""projectMailAdmin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static

from yandex import views
from . import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.login, name='login'),
    url(r'^emails/$', views.index, name='home'),
    url(r'^upds/$', views.upds, name='upds'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^update_db/$', views.parser, name='update_db'),
    # url(r'^get_detail/$', views.get_detail, name='detail'),
    url(r'^reg_user_token/$', views.reg_user_token, name='reg_user_token'),
    url(r'^edit_user/$', views.edit_user, name='edit_user'),
    #url(r'^get_login/(?P<logins>[^/]+)$', views.get_login, name='get_login'),
    url(r'^delete_user/$', views.delete_user, name='delete_user'),
    url(r'^set_forward/$', views.set_forward, name='set_forward'),
    url(r'^del_forward/(?P<login>[^/]+)/(?P<id_fw>\d+)$', views.del_forward, name='del_forward'),
    url(r'^del_forw/$', views.del_forw, name='del_forw'),

    url(r'^render_to_json/$', views.render_to_json, name='render_to_json'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
