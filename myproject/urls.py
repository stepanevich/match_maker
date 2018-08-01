from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from .myapp import views

from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^myapp/', views.list, name='list'),
    url(r'^filename/', views.filename, name='filename'),
    #url(r'^$', RedirectView.as_view(url='/myapp/list/', permanent=True)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
