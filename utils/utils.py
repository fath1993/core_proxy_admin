import random
import string
import secrets


def random_name():
    return "".join(random.choices(string.ascii_lowercase, k=6))


def random_password():
    return secrets.token_hex(4)


def create_json(method, request, result, message):
    body = {
        'method': method,
        'request': request,
        'result': result,
        'message': message
    }
    return body