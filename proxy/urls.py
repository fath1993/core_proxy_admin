from django.urls import path
from proxy.views import ProxyListView

app_name = 'proxies'

urlpatterns = (
    path('api/proxy-list/', ProxyListView.as_view(), name='proxy-list'),
)
