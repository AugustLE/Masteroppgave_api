from django.conf.urls import url
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf import settings
from django.conf.urls.static import static

app_name = 'staff'

urlpatterns = [

    url(r'^staff/subjects/$', views.SubjectList.as_view()),
    url(r'^staff/overview/$', views.Overview.as_view()),
    url(r'^staff/teams/$', views.TeamList.as_view()),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns = format_suffix_patterns(urlpatterns)