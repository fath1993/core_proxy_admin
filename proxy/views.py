from django.http import JsonResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from knox.auth import TokenAuthentication
from rest_framework.views import APIView
from proxy.models import Proxy
from proxy.serializer import ProxySerializer
from utils.utils import create_json


class ProxyListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {'detail': 'لیست پراکسی فعال'}

    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            proxies = Proxy.objects.filter(is_active=True)
        else:
            proxies = Proxy.objects.filter(is_active=True, belong_to=request.user)
        if proxies.count() == 0:
            return JsonResponse(
                create_json('post', 'لیست پراکسی فعال', 'ناموفق', f'پراکسی فعال یافت نشد'))

        serializer = ProxySerializer(proxies, many=True)
        result_data = serializer.data
        json_response_body = {
            'method': 'post',
            'request': 'لیست پراکسی فعال',
            'result': 'موفق',
            'data': result_data,
        }
        return JsonResponse(json_response_body)

    def put(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def delete(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})
