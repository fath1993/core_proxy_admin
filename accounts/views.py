import json
import jdatetime
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from knox.models import AuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from knox.auth import TokenAuthentication
from rest_framework.views import APIView
from django.contrib.auth.signals import user_logged_out
from accounts.models import Profile
from accounts.serializer import ProfileSerializer
from utils.utils import create_json


class AuthSimple(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {'detail': 'دریافت توکن با استفاده از نام کاربری و کلمه عبور'}

    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def post(self, request, *args, **kwargs):
        try:
            front_input = json.loads(request.body)
            try:
                username = front_input['username']
                password = front_input['password']
                if username is None:
                    print('نام کاربری خالی است')
                    return JsonResponse(create_json('post', 'دریافت توکن', 'ناموفق', f'نام کاربری خالی است'))
                if password is None:
                    print('کلمه عبور خالی است')
                    return JsonResponse(create_json('post', 'دریافت توکن', 'ناموفق', f'کلمه عبور خالی است'))
                try:
                    user = User.objects.get(username=username)
                    user = authenticate(request=request, username=username, password=password)
                    if not user:
                        print('رمز عبور صحیح نیست')
                        return JsonResponse(create_json('post', 'دریافت توکن', 'ناموفق',
                                                        f'رمز عبور صحیح نیست'))
                    token = AuthToken.objects.create(user)
                    json_response_body = {
                        'method': 'post',
                        'request': 'دریافت توکن',
                        'result': 'موفق',
                        'token': token[1],
                        'message': f"این توکن به مدت {str(settings.REST_KNOX['TOKEN_TTL'])} روز اعتبار خواهد داشت"
                    }
                    return JsonResponse(json_response_body)
                except Exception as e:
                    print(str(e))
                    return JsonResponse(create_json('post', 'دریافت توکن', 'ناموفق',
                                                    f'نام کاربری ارائه شده با مقدار {username} در سامانه موجود نیست'))
            except Exception as e:
                print(str(e))
                return JsonResponse(
                    create_json('post', 'دریافت توکن', 'ناموفق', f'نام کاربری یا رمز عبور بدرستی ارسال نشده است '))
        except Exception as e:
            print(str(e))
            return JsonResponse(create_json('post', 'دریافت توکن', 'ناموفق', f'ورودی صحیح نیست.'))

    def put(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def delete(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})


class AuthEliminateALL(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {'detail': 'ابطال توکن های فعال کاربر'}

    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def post(self, request, *args, **kwargs):
        try:
            front_input = json.loads(request.body)
            try:
                eliminate_all = front_input['eliminate_all']
                if eliminate_all is None:
                    print('نوع ابطال مشخص نشده است')
                    return JsonResponse(create_json('post', 'ابطال توکن', 'ناموفق', f'نوع ابطال مشخص نشده است'))
                eliminate_all = str(eliminate_all).lower()
                if eliminate_all == 'true' or eliminate_all == 'false':
                    print('نوع ابطال مشخص نشده است')
                    if eliminate_all == 'true':
                        try:
                            request._auth.delete()
                            user_logged_out.send(sender=request.user.__class__,
                                                 request=request, user=request.user)
                        except:
                            pass
                    else:
                        try:
                            request.user.auth_token_set.all().delete()
                            user_logged_out.send(sender=request.user.__class__,
                                                 request=request, user=request.user)
                        except:
                            pass
                    json_response_body = {
                        'method': 'post',
                        'request': 'ابطال توکن',
                        'result': 'موفق',
                        'eliminate_all': eliminate_all,
                    }
                    return JsonResponse(json_response_body)
                else:
                    print('تنها عبارات true یا false برای نوع ابطال مجاز می باشد')
                    return JsonResponse(create_json('post', 'ابطال توکن', 'ناموفق',
                                                    f'تنها عبارات true یا false برای نوع ابطال مجاز می باشد'))
            except Exception as e:
                print(str(e))
                return JsonResponse(
                    create_json('post', 'ابطال توکن', 'ناموفق', f'ورودی صحیح نیست یا بدرستی ارسال نشده است '))
        except Exception as e:
            print(str(e))
            return JsonResponse(create_json('post', 'ابطال توکن', 'ناموفق', f'ورودی صحیح نیست.'))

    def put(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def delete(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})


class Account(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {'detail': 'عملیات حساب کاربری'}

    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def post(self, request, *args, **kwargs):
        profile = Profile.objects.filter(user=request.user)
        if profile.count() == 0:
            return JsonResponse(
                create_json('post', 'جزئیات حساب کاربری', 'ناموفق', f'حساب کاربری یافت نشد'))
        serializer = ProfileSerializer(profile, many=True)
        profile = profile[0]
        if not profile.panel:
            return JsonResponse(
                create_json('post', 'جزئیات حساب کاربری', 'ناموفق', f'کابر پنل ندارد'))
        else:
            now = jdatetime.datetime.now()
            if (profile.updated_at + jdatetime.timedelta(days=profile.panel.deadline)) < now:
                profile.panel = None
                profile.save()
                return JsonResponse(
                    create_json('post', 'جزئیات حساب کاربری', 'ناموفق', f'پنل کابر منقضی شده است'))

        result_data = serializer.data
        json_response_body = {
            'method': 'post',
            'request': 'جزئیات حساب کاربری',
            'result': 'موفق',
            'data': result_data,
        }
        return JsonResponse(json_response_body)

    def put(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def delete(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})
