from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from food.views import  *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', logout_view),
    path('register/',register_view),
    path('menu/',menu_view,name='menu'),
    path('',include('food.urls')),
    path('story/', my_story, name='story'),
    path('',home)
    
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
