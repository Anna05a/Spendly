import monobank
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from monobank import Client
from datetime import datetime, date, timezone
from API.models import Card


@login_required(login_url='/login')
def home(request):
    return render(request,'main/main_new.html')

def statistics(request):
    return render(request, 'main/statistic_new.html')

@login_required(login_url='/login')
def statistics_page(request):
    return render(request, 'main/statistic_page.html')

@login_required(login_url='/login')
def home_page(request):
    return render(request, 'main/main_page.html')


# def add_card(request):
#     if request.method == 'POST':
#         form=TokenForm(request.POST)
#         try:
#             token=request.POST.get('token')
#             card_data=get_cards()
#             card_number = card_info[1]
#             card_balance = card_info[2]
#
#             card_obj = Card( balance=card_balance, card_number=card_number)
#             card_obj.save()
#             context = { 'balance': card_balance, 'number': card_number}
#             return render(request, 'main/main_page.html', context)
#         except Exception as e:
#             print(e)
#             return render(request, 'main/statistic_page.html')
#         context = {'form': form}
#         return render(request, 'main/main_new.html', context)
#
def get_token(request):
    token = request.POST.get('token')
    return token

card_ids = []
def add_card(request):
    token = get_token(request)
    try:
        client = Client(token)
        user_info = client.get_client_info()

        if user_info:
            for user in user_info['accounts']:
                originBalance = user['balance'] // 100
                card_balance=originBalance
                card_number=user['maskedPan'][0]
                card_ids.append(user['id'])
                card_obj = Card(id=card_ids,balance=card_balance, card_number=card_number)
                card_obj.save()
            context = {'balance': card_balance, 'number': card_number}
            return render(request, 'main/main_page.html', context)
    except Exception as e:
        print("Помилка у функції get_cards:", e)
        return render(request, 'main/main_new.html')

def get_pay(request, user_ids):
    token=get_token()
    mono = monobank.Client(token)
    originAmounts = []
    try:
        for user_id in user_ids:
            client = mono.get_statements(user_id, date(2024, 2, 23), date(2024, 2, 23))
            for payment in client:
                timeOrigin = datetime.fromtimestamp(payment['time'], timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                time=timeOrigin #Час
                originAmount = payment['amount'] // 100
                amount = originAmount #сума
                category=payment['description']
                if category == '':
                    category = 'no spendings'
                originAmounts.append(originAmount)
                currency = payment['currencyCode'] #валюта
        context={'amounts': amount, 'category': category, 'time': time, 'currency': currency}
    except Exception as e:
        print("Помилка у функції get_pay:", e)
        return render(request, 'main/statistic_page.html')
    return render(request, 'main/main_page.html', context)
