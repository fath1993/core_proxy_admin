import json
import random
import uuid

import jdatetime
import requests
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from knox.models import AuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from knox.auth import TokenAuthentication
from rest_framework.views import APIView
from django.contrib.auth.signals import user_logged_out
from accounts.models import Profile, SMSAuthCode, Order, Transaction, PaymentCode
from accounts.serializer import ProfileSerializer
from batobox.settings import BASE_URL, ZARINPAL_API_KEY
from custom_logs.models import custom_log
from utilities.http_metod import fetch_data_from_http_post, fetch_single_file_from_http_files
from utilities.send_sms import SendVerificationSMSThread
from utilities.utilities import create_json


def test_view(request):
    return render(request, 'test.html')


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


class AuthSMSRequest(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {'detail': 'ارسال درخواست دریافت توکن از طریق شماره همراه'}

    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def post(self, request, *args, **kwargs):
        try:
            front_input = json.loads(request.body)
            try:
                phone_number = front_input['phone_number']
                if phone_number is None:
                    print('شماره همراه خالی است')
                    return JsonResponse(create_json('post', 'ارسال درخواست دریافت توکن با شماره همراه', 'ناموفق',
                                                    f'شماره همراه خالی است'))
                try:
                    user = User.objects.get(username=phone_number)
                    try:
                        sms_auth_code = SMSAuthCode.objects.get(phone_number=phone_number)
                        time_spent = (jdatetime.datetime.now() - sms_auth_code.created_at).total_seconds()
                        if time_spent <= 120:
                            print('از ارسال پیامک قبلی کمتر از دو دقیقه گذشته است')
                            return JsonResponse(
                                create_json('post', 'ارسال درخواست دریافت توکن با شماره همراه', 'ناموفق',
                                            f'ارسال درخواست مجدد پس از {120 - time_spent} ثانیه'))
                        else:
                            sms_auth_code.delete()
                    except Exception as e:
                        pass
                    random_otp = random.randint(100000, 999999)
                    new_sms_auth_code = SMSAuthCode.objects.create(
                        phone_number=phone_number,
                        pass_code=random_otp,
                    )
                    SendVerificationSMSThread(phone_number, '922176', f'{random_otp}').start()
                    json_response_body = {
                        'method': 'post',
                        'request': 'ارسال درخواست دریافت توکن با شماره همراه',
                        'result': 'موفق',
                        'message': f'کد تایید یک بار مصرف به شماره {phone_number} پیامک شد و تا 2 دقیقه معتبر می باشد',
                    }
                    return JsonResponse(json_response_body)
                except Exception as e:
                    print(str(e))
                    return JsonResponse(create_json('post', 'ارسال درخواست دریافت توکن با شماره همراه', 'ناموفق',
                                                    f'شماره همراه با مقدار {phone_number} در سامانه موجود نیست'))
            except Exception as e:
                print(str(e))
                return JsonResponse(create_json('post', 'ارسال درخواست دریافت توکن با شماره همراه', 'ناموفق',
                                                f'داده های ورودی کامل نیست یا بدرستی ارسال نشده است'))
        except Exception as e:
            print(str(e))
            return JsonResponse(
                create_json('post', 'ارسال درخواست دریافت توکن با شماره همراه', 'ناموفق', f'ورودی صحیح نیست.'))

    def put(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def delete(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})


class AuthSMSValidate(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {'detail': 'دریافت توکن با استفاده از شماره همراه و کد پیامکی'}

    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def post(self, request, *args, **kwargs):
        try:
            front_input = json.loads(request.body)
            try:
                phone_number = front_input['phone_number']
                validate_code = front_input['validate_code']
                if phone_number is None:
                    print('شماره همراه خالی است')
                    return JsonResponse(create_json('post', 'دریافت توکن', 'ناموفق', f'نام کاربری خالی است'))
                if validate_code is None:
                    print('کد پیامکی خالی است')
                    return JsonResponse(create_json('post', 'دریافت توکن', 'ناموفق', f'کلمه عبور خالی است'))
                try:
                    user = User.objects.get(username=phone_number)
                    sms_auth_codes = SMSAuthCode.objects.filter(phone_number=phone_number)
                    if sms_auth_codes.count() == 0:
                        return JsonResponse(create_json('post', 'دریافت توکن', 'ناموفق',
                                                        f'کد پیامکی با مقدار {validate_code} اشتباه است'))
                    else:
                        sms_auth_code = sms_auth_codes.latest('created_at')
                    time_spent = (jdatetime.datetime.now() - sms_auth_code.created_at).total_seconds()
                    if time_spent > 120:
                        print('از ارسال پیامک قبلی بیشتر از دو دقیقه گذشته است')
                        return JsonResponse(
                            create_json('post', 'دریافت توکن', 'ناموفق',
                                        f'کد پیامکی با مقدار {validate_code} منقضی شده است'))
                    else:
                        if str(validate_code) == sms_auth_code.pass_code:
                            token = AuthToken.objects.create(user)
                            json_response_body = {
                                'method': 'post',
                                'request': 'دریافت توکن',
                                'result': 'موفق',
                                'token': token[1],
                                'message': f"این توکن به مدت {str(settings.REST_KNOX['TOKEN_TTL'])} روز اعتبار خواهد داشت"
                            }
                            for sms_validation_item in sms_auth_codes:
                                sms_validation_item.delete()
                            return JsonResponse(json_response_body)
                        else:
                            return JsonResponse(create_json('post', 'دریافت توکن', 'ناموفق',
                                                            f'کد پیامکی با مقدار {validate_code} اشتباه است'))
                except Exception as e:
                    print(str(e))
                    return JsonResponse(create_json('post', 'دریافت توکن', 'ناموفق',
                                                    f'شماره همراه ارائه شده با مقدار {phone_number} در سامانه موجود نیست'))
            except Exception as e:
                print(str(e))
                return JsonResponse(
                    create_json('post', 'دریافت توکن', 'ناموفق', f'داده های ورودی کامل نیست یا بدرستی ارسال نشده است '))
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


class Register(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {'detail': 'درخواست ثبت نام و تایید پیامکی'}

    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def post(self, request, *args, **kwargs):
        try:
            front_input = json.loads(request.body)
            try:
                try:
                    phone_number = front_input['phone_number']
                    if phone_number == '':
                        phone_number = None
                except:
                    phone_number = None
                if not phone_number:
                    print('شماره همراه خالی است')
                    return JsonResponse(create_json('post', 'درخواست ثبت نام', 'ناموفق', f'شماره همراه خالی است'))
                try:
                    password = front_input['password']
                    if password == '':
                        password = None
                except:
                    password = None
                if not password:
                    print('کلمه عبور خالی است')
                    return JsonResponse(create_json('post', 'درخواست ثبت نام', 'ناموفق', f'کلمه عبور خالی است'))
                if len(str(password)) < 8:
                    print('کلمه عبور کمتر از 8 کاراکتر است')
                    return JsonResponse(
                        create_json('post', 'درخواست ثبت نام', 'ناموفق', f'کلمه عبور کمتر از 8 کاراکتر است'))

                try:
                    first_name = front_input['first_name']
                    if first_name == '':
                        first_name = None
                except:
                    first_name = None
                try:
                    last_name = front_input['last_name']
                    if last_name == '':
                        last_name = None
                except:
                    last_name = None
                try:
                    email = front_input['email']
                    if email == '':
                        email = None
                except:
                    email = None
                try:
                    birthday = front_input['birthday']
                    if birthday == '':
                        birthday = None
                except:
                    birthday = None
                try:
                    province = front_input['province']
                    if province == '':
                        province = None
                except:
                    province = None
                try:
                    city = front_input['city']
                    if city == '':
                        city = None
                except:
                    city = None
                try:
                    address = front_input['address']
                    if address == '':
                        address = None
                except:
                    address = None
                try:
                    zip_code = front_input['zip_code']
                    if zip_code == '':
                        zip_code = None
                except:
                    zip_code = None

                if birthday:
                    try:
                        birthday = str(birthday).split('/')
                        birthday = jdatetime.datetime(year=int(birthday[0]), month=int(birthday[1]),
                                                      day=int(birthday[2]))
                    except Exception as e:
                        print(e)
                        print('تاریخ تولد بدرستی ارسال نشده است')
                        return JsonResponse(create_json('post', 'درخواست ثبت نام', 'ناموفق',
                                                        f'تاریخ تولد ارسالی با مقدار {birthday} صحیح نیست'))
                try:
                    user = User.objects.get(username=phone_number)
                    profile = user.user_profile
                    if user.is_active:
                        print(f'اکانت مورد درخواست با شماره {phone_number} سامانه ثبت شده است')
                        return JsonResponse(create_json('post', 'درخواست ثبت نام', 'ناموفق',
                                                        f'اکانت مورد درخواست با شماره {phone_number} سامانه ثبت شده است'))
                    else:
                        if birthday:
                            profile.birthday = birthday
                        if first_name:
                            profile.first_name = first_name
                        if last_name:
                            profile.last_name = last_name
                        if province:
                            profile.province = province
                        if city:
                            profile.city = city
                        if address:
                            profile.address = address
                        if zip_code:
                            profile.zip_code = zip_code
                        profile.save()
                        try:
                            sms_auth_code = SMSAuthCode.objects.get(phone_number=phone_number)
                            time_spent = (jdatetime.datetime.now() - sms_auth_code.created_at).total_seconds()
                            if time_spent <= 120:
                                print('از ارسال پیامک قبلی کمتر از دو دقیقه گذشته است')
                                return JsonResponse(
                                    create_json('post', 'درخواست ثبت نام', 'ناموفق',
                                                f'ارسال درخواست مجدد پس از {120 - time_spent} ثانیه'))
                            else:
                                sms_auth_code.delete()
                        except Exception as e:
                            pass
                        random_otp = random.randint(100000, 999999)
                        new_sms_auth_code = SMSAuthCode.objects.create(
                            phone_number=phone_number,
                            pass_code=random_otp,
                        )
                        SendVerificationSMSThread(phone_number, '681425', f'{random_otp}').start()
                        json_response_body = {
                            'method': 'post',
                            'request': 'درخواست ثبت نام',
                            'result': 'موفق',
                            'message': 'پیامک تایید به شماره همراه پیامک شد',
                        }
                        return JsonResponse(json_response_body)
                except:
                    try:
                        sms_auth_code = SMSAuthCode.objects.get(phone_number=phone_number)
                        time_spent = (jdatetime.datetime.now() - sms_auth_code.created_at).total_seconds()
                        if time_spent <= 120:
                            print('از ارسال پیامک قبلی کمتر از دو دقیقه گذشته است')
                            return JsonResponse(
                                create_json('post', 'درخواست ثبت نام', 'ناموفق',
                                            f'ارسال درخواست مجدد پس از {120 - time_spent} ثانیه'))
                        else:
                            sms_auth_code.delete()
                    except Exception as e:
                        pass
                    user = User.objects.create_user(
                        username=phone_number,
                        password=password,
                        email=email,
                        is_active=False,
                    )
                    profile = user.user_profile
                    if birthday:
                        profile.birthday = birthday
                    if first_name:
                        profile.first_name = first_name
                    if last_name:
                        profile.last_name = last_name
                    if province:
                        profile.province = province
                    if city:
                        profile.city = city
                    if address:
                        profile.address = address
                    if zip_code:
                        profile.zip_code = zip_code
                    profile.save()
                    random_otp = random.randint(100000, 999999)
                    new_sms_auth_code = SMSAuthCode.objects.create(
                        phone_number=phone_number,
                        pass_code=random_otp,
                    )
                    SendVerificationSMSThread(phone_number, '681425', f'{random_otp}').start()
                    json_response_body = {
                        'method': 'post',
                        'request': 'درخواست ثبت نام',
                        'result': 'موفق',
                        'message': 'پیامک تایید به شماره همراه پیامک شد',
                    }
                    return JsonResponse(json_response_body)
            except Exception as e:
                print(str(e))
                return JsonResponse(
                    create_json('post', 'درخواست ثبت نام', 'ناموفق', f'داده های ورودی بدرستی ارسال نشده است '))
        except Exception as e:
            print(str(e))
            return JsonResponse(create_json('post', 'درخواست ثبت نام', 'ناموفق', f'ورودی صحیح نیست.'))

    def put(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def delete(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})


class RegisterConfirm(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {'detail': 'درخواست تایید ثبت نام'}

    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def post(self, request, *args, **kwargs):
        try:
            front_input = json.loads(request.body)
            try:
                phone_number = front_input['phone_number']
                verify_code = front_input['verify_code']
                if phone_number is None:
                    print('شماره همراه خالی است')
                    return JsonResponse(create_json('post', 'درخواست تایید ثبت نام', 'ناموفق', f'شماره همراه خالی است'))
                if verify_code is None:
                    print('کد پیامکی خالی است')
                    return JsonResponse(create_json('post', 'درخواست تایید ثبت نام', 'ناموفق', f'کد پیامکی خالی است'))
                try:
                    sms_auth_code = SMSAuthCode.objects.get(phone_number=phone_number)
                    if not verify_code == sms_auth_code.pass_code:
                        print('شماره همراه در سامانه موجود نیست')
                        return JsonResponse(
                            create_json('post', 'درخواست تایید ثبت نام', 'ناموفق',
                                        f'کد پیامکی با مقدار {verify_code} صحیح نیست'))
                    try:
                        user = User.objects.get(username=phone_number)
                        user.is_active = True
                        user.save()
                        sms_auth_code.delete()
                        token = AuthToken.objects.create(user)
                        json_response_body = {
                            'method': 'post',
                            'request': 'درخواست تایید ثبت نام',
                            'result': 'موفق',
                            'token': token[1],
                            'message': f"ثبت نام تایید و حساب کاربری فعال گردید. این توکن به مدت {str(settings.REST_KNOX['TOKEN_TTL'])} فعال خواهد بود.",
                        }
                        return JsonResponse(json_response_body)
                    except:
                        print('شماره همراه در سامانه موجود نیست')
                        return JsonResponse(
                            create_json('post', 'درخواست تایید ثبت نام', 'ناموفق',
                                        f'شماره همراه با مقدار {phone_number} سامانه موجود نیست'))
                except Exception as e:
                    print(f'درخواست ثبت نام برای شماره {phone_number} ثبت نشده است')
                    return JsonResponse(create_json('post', 'درخواست تایید ثبت نام', 'ناموفق',
                                                    f'درخواست ثبت نام برای شماره {phone_number} ثبت نشده است'))
            except Exception as e:
                print(str(e))
                return JsonResponse(
                    create_json('post', 'درخواست تایید ثبت نام', 'ناموفق',
                                f'ورودی صحیح نیست یا بدرستی ارسال نشده است '))
        except Exception as e:
            print(str(e))
            return JsonResponse(create_json('post', 'درخواست تایید ثبت نام', 'ناموفق', f'ورودی صحیح نیست.'))

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
        result_data = serializer.data
        for data in result_data:
            data['email'] = request.user.email
        json_response_body = {
            'method': 'post',
            'request': 'جزئیات حساب کاربری',
            'result': 'موفق',
            'data': result_data,
        }
        return JsonResponse(json_response_body)

    def put(self, request, *args, **kwargs):
        try:
            front_input = json.loads(request.body)
            try:
                phone_number = front_input['phone_number']
            except:
                phone_number = None
            try:
                password = front_input['password']
            except:
                password = None
            try:
                first_name = front_input['first_name']
            except:
                first_name = None
            try:
                last_name = front_input['last_name']
            except:
                last_name = None
            try:
                national_code = front_input['national_code']
            except:
                national_code = None
            try:
                landline = front_input['landline']
            except:
                landline = None
            try:
                email = front_input['email']
            except:
                email = None
            try:
                birthday = front_input['birthday']
            except:
                birthday = None
            try:
                location_details = front_input['location_details']
            except:
                location_details = None
            try:
                card_number = front_input['card_number']
            except:
                card_number = None
            try:
                isbn = front_input['isbn']
            except:
                isbn = None
            try:
                like_list = front_input['like_list']
            except:
                like_list = None
            try:
                wish_list = front_input['wish_list']
            except:
                wish_list = None
            try:
                temp_card = front_input['temp_card']
            except:
                temp_card = None
            user = request.user
            profile = user.user_profile
            if password:
                if password == '':
                    print('کلمه عبور خالی است')
                    return JsonResponse(
                        create_json('post', 'درخواست ویرایش اطلاعات حساب', 'ناموفق', f'کلمه عبور خالی است'))
                if len(str(password)) < 8:
                    print('کلمه عبور کمتر از 8 کاراکتر است')
                    return JsonResponse(create_json('post', 'درخواست ویرایش اطلاعات حساب', 'ناموفق',
                                                    f'کلمه عبور کمتر از 8 کاراکتر است'))
                user.set_password(str(password))
            if email:
                user.email = email
            user.save()
            if phone_number:
                profile.mobile_phone_number = phone_number
            if birthday:
                print(birthday)
                try:
                    birthday = str(birthday).split('/')
                    birthday = jdatetime.datetime(year=int(birthday[0]), month=int(birthday[1]),
                                                  day=int(birthday[2]))
                    profile.birthday = birthday
                except Exception as e:
                    print(e)
                    print('تاریخ تولد بدرستی ارسال نشده است')
                    return JsonResponse(create_json('post', 'درخواست ویرایش اطلاعات حساب', 'ناموفق',
                                                    f'تاریخ تولد ارسالی با مقدار {birthday} صحیح نیست'))
            if first_name:
                profile.first_name = first_name
            if last_name:
                profile.last_name = last_name
            if landline:
                profile.landline = landline
            if national_code:
                profile.national_code = national_code
            if card_number:
                profile.card_number = card_number
            if isbn:
                profile.isbn = isbn
            if location_details:
                profile.location_details = location_details
            if like_list:
                profile.like_list = like_list
            if wish_list:
                profile.wish_list = wish_list
            if temp_card:
                profile.temp_card = temp_card
            profile.save()

            profile = Profile.objects.filter(user=request.user)
            if profile.count() == 0:
                return JsonResponse(
                    create_json('post', 'ویرایش حساب کاربری', 'ناموفق', f'حساب کاربری یافت نشد'))
            serializer = ProfileSerializer(profile, many=True)
            result_data = serializer.data
            for data in result_data:
                data['email'] = request.user.email
            json_response_body = {
                'method': 'put',
                'request': 'ویرایش حساب کاربری',
                'result': 'موفق',
                'data': serializer.data,
            }
            return JsonResponse(json_response_body)

        except Exception as e:
            print(str(e))
            return JsonResponse(create_json('post', 'درخواست ویرایش اطلاعات حساب', 'ناموفق', f'ورودی صحیح نیست.'))

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        json_response_body = {
            'method': 'post',
            'request': 'حذف حساب کاربری',
            'result': 'موفق',
        }
        return JsonResponse(json_response_body)


class WalletChargeView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def __init__(self):
        super().__init__()

    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def post(self, request, *args, **kwargs):
        try:
            front_input = json.loads(request.body)
            try:
                amount = front_input['amount']

                new_order = Order.objects.create(
                    order_status='در حال بررسی',
                    description='شارژ اعتبار حساب',
                    first_name=request.user.user_profile.first_name,
                    last_name=request.user.user_profile.last_name,
                    national_code=request.user.user_profile.national_code,
                    email=request.user.email,
                    mobile_phone_number=request.user.username,
                    landline=request.user.user_profile.landline,
                    card_number=request.user.user_profile.card_number,
                    isbn=request.user.user_profile.isbn,
                    receiver_province='-',
                    receiver_city='-',
                    receiver_zip_code='-',
                    receiver_address='-',
                    receiver_mobile_phone_number='-',
                    created_by=request.user,
                    updated_by=request.user,
                )
                try:
                    amount = int(amount)
                    if amount < 10000:
                        return JsonResponse(
                            create_json('post', 'درخواست شارژ اعتبار حساب', 'ناموفق',
                                        f'حداقل میزان شارژ اعتبار حساب 10 هزار تومان می باشد'))
                except:
                    return JsonResponse(
                        create_json('post', 'درخواست شارژ اعتبار حساب', 'ناموفق',
                                    f'amount ارسالی با مقدار {amount} صحیح نیست'))
                try:
                    url = 'https://api.zarinpal.com/pg/v4/payment/request.json'
                    header = {'Content-Type': 'application/json', 'accept': 'application/json'}
                    data = {
                        "merchant_id": ZARINPAL_API_KEY,
                        "amount": amount * 10,
                        "description": f"فاکتور پرداختی توسط {request.user.username}",
                        "callback_url": f'{BASE_URL}store/api/pay-confirm/',
                        "metadata": {"mobile": request.user.username}
                    }
                    pay_request = requests.post(url=url, json=data, headers=header)
                    try:
                        if pay_request.status_code == 200:
                            authority = pay_request.json()['data']["authority"]
                            try:
                                payment_code = PaymentCode.objects.filter(unique_code=authority)
                                if payment_code.count() == 0:
                                    raise Exception
                                else:
                                    payment_code.delete()
                            except:
                                payment_code = PaymentCode.objects.create(
                                    user=request.user,
                                    unique_code=authority,
                                    is_used=False,
                                )
                            new_transaction = Transaction.objects.create(
                                order=new_order,
                                amount=amount,
                                description='شارژ اعتبار حساب',
                                email=request.user.email,
                                mobile=request.user.username,
                                authority=authority,
                                ref_id='شارژ اعتبار حساب',
                                status='پرداخت نشده',
                            )
                            json_response_body = {
                                'method': 'post',
                                'request': 'درخواست شارژ اعتبار حساب',
                                'result': 'موفق',
                                'order_detail': {
                                    'products': 'شارژ اعتبار حساب',
                                    'order_status': 'در حال بررسی',
                                    'created_at': str(new_order.created_at),
                                    'updated_at': str(new_order.updated_at),
                                    'created_by': new_order.created_by.username,
                                    'updated_by': new_order.updated_by.username,
                                },
                                'transaction_detail': {
                                    'transaction_id': new_transaction.id,
                                    'payment_unique_code': authority
                                }
                            }
                            return JsonResponse(json_response_body)
                        else:
                            return JsonResponse(
                                create_json('post', 'درخواست شارژ اعتبار حساب', 'ناموفق',
                                            f'خطای بازگشتی از درگاه پرداخت زرینپال با کد {pay_request.status_code}'))
                    except Exception as e:
                        print(str(e))
                        return JsonResponse(
                            create_json('post', 'درخواست شارژ اعتبار حساب', 'ناموفق',
                                        f'ارتباط با درگاه پرداخت زرین پال ممکن نیست'))
                except Exception as e:
                    print(str(e))
                    return JsonResponse(
                        create_json('post', 'درخواست شارژ اعتبار حساب', 'ناموفق', f'ارتباط با درگاه پرداخت زرین پال ممکن نیست'))
            except Exception as e:
                print(str(e))
                return JsonResponse(
                    create_json('post', 'درخواست شارژ اعتبار حساب', 'ناموفق', f'داده ورودی کامل ارسال نشده است'))
        except Exception as e:
            print(str(e))
            return JsonResponse(create_json('post', 'درخواست شارژ اعتبار حساب', 'ناموفق', f'ورودی صحیح نیست.'))

    def put(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def delete(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})





