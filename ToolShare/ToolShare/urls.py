from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

admin.autodiscover()
from login.views import logoutUser, home
from shareCenter.views import toolDirectory

urlpatterns = [
    path('registration/', include('registration.urls', namespace='registration')),
    path('login/', include('login.urls', namespace='login')),
    path('logout/', logoutUser),
    path('home/', home),
    path('sharecenter/', include('shareCenter.urls', namespace='sharecenter')),
    path('tooldirectory/', toolDirectory),
    path('messagecenter/', include('messageCenter.urls', namespace='messagecenter')),
    path('communitystats/', include('communityStats.urls', namespace='communitystats')),
    path('admin/', admin.site.urls),
    path('', home),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
