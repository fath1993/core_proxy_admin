import json
import requests
from core.settings import BASE_DIR, BASE_URL


def test_auth_simple(username, password):
    url = f'{BASE_URL}account/api/auth-simple/'
    data = {
        'username': f'{username}',
        'password': f'{password}',
    }
    try:
        response = requests.post(url=url, json=data)
        print(json.loads(response.content))
    except Exception as e:
        print(str(e))


def test_auth_eliminate_all(eliminate_all_1, user_active_token_1):
    url = f'{BASE_URL}account/api/auth-eliminate-all/'
    headers = {
        'Authorization': f'BatoboxToken {user_active_token_1}'
    }
    data = {
        'eliminate_all': f'{eliminate_all_1}',
    }
    try:
        response = requests.post(url=url, headers=headers, json=data)
        print(json.loads(response.content))
    except Exception as e:
        print(str(e))



def test_account(user_active_token, method_name):
    url = f'{BASE_URL}account/api/account/'
    headers = {
        'Authorization': f'BatoboxToken {user_active_token}'
    }
    if method_name == 'post':
        try:
            response = requests.post(url=url, headers=headers)
            print(json.loads(response.content))
        except Exception as e:
            print(str(e))
    elif method_name == 'put':
        data = {
            'first_name': 'امیرحسین',
            'last_name': 'بارانی',
            'birthday': '1372/05/23',
        }
        try:
            response = requests.put(url=url, headers=headers, json=data)
            print(json.loads(response.content))
        except Exception as e:
            print(str(e))
    elif method_name == 'delete':
        try:
            response = requests.delete(url=url, headers=headers)
            print(json.loads(response.content))
        except Exception as e:
            print(str(e))
