from django.conf.urls import url
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf import settings
from django.conf.urls.static import static

app_name = 'student'

urlpatterns = [

    #url(r'^subject/(?P<subject_id>[0-9]+)/teams/$', views.TeamList.as_view()),
    url(r'^subject/teams/$', views.TeamList.as_view()),
    url(r'^subject/selectteam/$', views.SelectTeam.as_view()),
    url(r'^team/status/$', views.TeamStatus.as_view()),
    url(r'^team/registerscore/$', views.RegisterScore.as_view()),
    url(r'^team/unregister/$', views.UnregisterFromTeam.as_view()),
    url(r'^team/contactinfo/$', views.ContactInfo.as_view()),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns = format_suffix_patterns(urlpatterns)