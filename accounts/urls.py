from django.urls import path, include

from accounts.views import AuthSimple, AuthSMSRequest, AuthSMSValidate, AuthEliminateALL, Register, RegisterConfirm, \
    Account, test_view, WalletChargeView

app_name = 'accounts'

urlpatterns = (
    # test
    path('test/', test_view, name='test'),

    # auth
    path('api/auth-simple/', AuthSimple.as_view(), name='api-auth-simple'),
    path('api/auth-sms-request/', AuthSMSRequest.as_view(), name='api-auth-sms-request'),
    path('api/auth-sms-validate/', AuthSMSValidate.as_view(), name='api-auth-sms-validate'),
    path('api/auth-eliminate-all/', AuthEliminateALL.as_view(), name='api-auth-eliminate-all'),

    # new account
    path('api/register/', Register.as_view(), name='api-register'),
    path('api/register-confirm/', RegisterConfirm.as_view(), name='api-register-confirm'),

    # account
    path('api/account/', Account.as_view(), name='account'),
    path('api/wallet-charge/', WalletChargeView.as_view(), name='wallet-charge'),
)
