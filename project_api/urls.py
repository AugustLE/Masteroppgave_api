from django.contrib import admin
from django.conf.urls import url, include

urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^', include('user.urls')),
    url(r'^', include('data.urls')),
    url(r'^', include('student.urls')),
    url(r'^', include('staff.urls'))

]
