from django.urls import path

from accounts.views import AuthSimple, AuthEliminateALL, Account

app_name = 'accounts'

urlpatterns = (
    # auth
    path('api/auth-simple/', AuthSimple.as_view(), name='api-auth-simple'),
    path('api/auth-eliminate-all/', AuthEliminateALL.as_view(), name='api-auth-eliminate-all'),

    # account
    path('api/account/', Account.as_view(), name='account'),
)
