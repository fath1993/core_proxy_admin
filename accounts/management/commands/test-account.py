from django.core.management import base

from accounts.tests import test_auth_simple, test_auth_eliminate_all, test_account


class Command(base.BaseCommand):
    def handle(self, *args, **options):
        while True:
            print('please choose a number:')
            print('1. test_auth_simple')
            print('2. test_auth_eliminate_all')
            print('3. test_account')
            try:
                choice = int(input())
                if choice == 1:
                    print('please input username:')
                    username = str(input())
                    print('please input password:')
                    password = str(input())
                    test_auth_simple(username, password)
                elif choice == 2:
                    print('please input user active token:')
                    user_active_token = str(input())
                    print('do you want to eliminate all session or current? true or false:')
                    eliminate_all = str(input())
                    if eliminate_all == 'true' or eliminate_all == 'false':
                        test_auth_eliminate_all(eliminate_all, user_active_token)
                    else:
                        print('not correct! try again')
                elif choice == 3:
                    print('please input user active token:')
                    user_active_token = str(input())
                    print('please input method name:')
                    method_name = str(input())
                    if method_name == 'post' or method_name == 'put' or method_name == 'delete':
                        test_account(user_active_token, method_name)
                    else:
                        print('not correct! try again')
                else:
                    print('wrong choice! try again')
            except:
                print('not correct! try again')
