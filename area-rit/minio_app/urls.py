from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from mozilla_django_oidc.views import OIDCAuthenticationRequestView, OIDCAuthenticationCallbackView
from file_manager.views import homepage_view, my_logout_view

urlpatterns = [
    path('', homepage_view, name='homepage'),
    path('admin/', admin.site.urls),
    path('files/', include('file_manager.urls')),
    #path('logout/', LogoutView.as_view(), name='logout'),
    path('logout/', my_logout_view, name='logout'),
    path("oidc/login/", OIDCAuthenticationRequestView.as_view(), name="oidc_login"),
    path('oidc/callback/', OIDCAuthenticationCallbackView.as_view(), name='oidc_authentication_callback'),
]
