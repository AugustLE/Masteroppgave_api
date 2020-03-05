from django.conf.urls import url
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf import settings
from django.conf.urls.static import static

app_name = 'staff'

urlpatterns = [

    url(r'^staff/overview/$', views.Overview.as_view()),
    url(r'^staff/teams/$', views.TeamList.as_view()),
    url(r'^staff/teams/(?P<team_id>[0-9]+)/$', views.TeamInfo.as_view()),
    url(r'^staff/teams/upload/$', views.TeamUploader.as_view()),
    url(r'^staff/requestauth/$', views.CheckAuthority.as_view()),
    url(r'^staff/getauth/$', views.CheckAuthority.as_view()),
    url(r'^staff/pinteam/$', views.PinTeam.as_view()),
    url(r'^staff/unpinteam/$', views.PinTeam.as_view()),
    url(r'^staff/teamhistory/(?P<team_id>[0-9]+)/$', views.TeamHistory.as_view()),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns = format_suffix_patterns(urlpatterns)