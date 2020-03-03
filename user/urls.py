from django.conf.urls import url

from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf import settings
from django.conf.urls.static import static

app_name = 'user'

urlpatterns = [

    url(r'^user/detail/$', views.UserDetail.as_view()),
    url(r'^user/feidelogin/$', views.CreateOrLoginUser.as_view()),
    url(r'^user/delete/$', views.DeleteUser.as_view()),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns = format_suffix_patterns(urlpatterns)