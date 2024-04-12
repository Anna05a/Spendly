# from django.shortcuts import render
# from monobank import Client
# import monobank
# from datetime import datetime, date, timezone
# import time
# card_info = []
# card_ids = []
# token = "uMFnniKt0wqgra57udOS-2LPZCidP6agFeZwyur8s8TE"
# mono = monobank.Client(token)
# def get_cards():
#     try:
#         mono = monobank.Client(token)
#         user_info = mono.get_client_info()

#         if user_info:

#             for user in user_info['accounts']:
#                # print(user_info)
#                 originBalance = user['balance'] // 100
#                 temp = user['maskedPan'][0]
#                 number=user['maskedPan']
#                 if temp[0] == '4':
#                     print('VISA ''Назва карти ', number, 'Номер карти ', number, 'Баланс по карті', originBalance)
#                 elif temp[0] == '5':
#                     print('Master ''Назва карти ', user['type'], 'Номер карти ', user['maskedPan'], 'Баланс по карті', originBalance)
#                 card_info.append(user['type'])
#                 card_info.append(user['maskedPan'])
#                 card_info.append(originBalance)
#                 card_data = []
#                 card_data.append(card_info)
#                 card_ids.append(user['id'])
#                 #print(card_info)
#                 #print(card_data)
#                 print(" ")
#                 #print(card_ids)
#                 #print(get_pay())
#         return card_ids, card_info
#     except Exception as e:
#         print("Помилка у функції get_cards:", e)
#         return []

# def get_pay( ):
#     payments=[]
#     originAmounts = []
#     try:
#         print(' ')
#         for id in card_ids:
#             for i in id:

#                 client = mono.get_statements('9OdmQNNQf9-WMd2AA0h_RA', date(2024, 4, 4), date(2024, 4, 5))
#                 for payment in client:
#                     print(client)
#                     timeOrigin = datetime.fromtimestamp(payment['time'], timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
#                     print('Час', timeOrigin)
#                     originAmount = payment['amount'] // 100
#                     print('Сума', originAmount)
#                     originAmounts.append(originAmount)
#                     print('Категорія', payment['description'])
#                     print('Валюта', payment['currencyCode'])

#                     print('--------------------------------------')
#     except Exception as e:
#         print("Помилка у функції get_pay:", e)
#     return originAmounts, payments

# def get_category_earn_cost(originAmounts):
#     token = 'token'
#     mono = monobank.Client(token)
#     try:
#         for originAmount in originAmounts:
#             if str(originAmount).startswith('-'):
#                 print("Витрата")
#             else:
#                 print("Поповнення")
#     except Exception as e:
#         print("Помилка у функції get_category_earn_cost:", e)

# try:
#     card_ids = get_cards()
#     get_cards()
#     if card_ids:
#         time.sleep(61)
#         originAmounts = get_pay()
#         time.sleep(100)
#         get_category_earn_cost(originAmounts)
# except Exception as e:
#     print("Помилка у головній програмі:", e)
