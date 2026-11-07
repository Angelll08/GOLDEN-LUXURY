from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/', include('cuentas.urls')),
    path('accounts/', include('allauth.urls')),   # callbacks de Google/Facebook
    path('panel/', include('panel.urls')),
    path('analitica/', include('analitica.urls')),
    path('', include('tienda.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Demo en Render: las fotos de productos se sirven desde la carpeta media del proyecto
    urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]
