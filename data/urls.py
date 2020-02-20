from django.conf.urls import url

from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf import settings
from django.conf.urls.static import static

app_name = 'data'

urlpatterns = [

    url(r'^selectsubject/$', views.SelectSubject.as_view()),
    url(r'^selectsubjectwithteams/$', views.SelectSubjectWithTeams.as_view()),
    url(r'^user/$', views.ApiUser.as_view()),
    ###
    url(r'^testdata/$', views.TestData.as_view()),
    url(r'^privacyconsent/(?P<username>\w+)/$', views.GetPrivacyConsent.as_view()),
    url(r'^privacyconsent/$', views.GetPrivacyConsent.as_view()),
    url(r'^subjectlist/$', views.SubjectList.as_view()),
    url(r'^teamlist/$', views.TeamList.as_view()),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns = format_suffix_patterns(urlpatterns)