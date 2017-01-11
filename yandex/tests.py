from django.test import TestCase

from urllib.request import urlopen

for i in range(20, 201):
    link = 'https://pddimp.yandex.ru/reg_user_token.xml?token=8ce7284484b2474857d17335c2acd0d2c4cc6203aaa4b743b1656bf3&u_login=test%s&u_password=12345qwert' % i
    urlopen(link)
    print('test'+str(i))

# for i in range(20, 201):
#     link = 'https://pddimp.yandex.ru/delete_user.xml?token=8ce7284484b2474857d17335c2acd0d2c4cc6203aaa4b743b1656bf3&login=test%s' % i
#     urlopen(link)
#     print('test'+str(i))