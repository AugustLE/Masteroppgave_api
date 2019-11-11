from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include('user.urls')),
    url(r'^', include('data.urls')),
    url(r'^', include('student.urls')),
    url(r'^', include('staff.urls'))

]
