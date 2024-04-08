import monobank
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from monobank import Client
from datetime import datetime, date, timezone
import time
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

def get_token(request):
    token = request.GET.get('token')
    return token
    return render(request,'main/main_new.html')

card_ids = []
def add_card(request):
    token = request.POST.get('token')
    mono = monobank.Client(token)
    originAmounts = []
    payments=[]
    labels = []
    data = []
    try:
        cards = []
        client = Client(token)
        user_info = client.get_client_info()
        #додавання карти
        if user_info:
            for user in user_info['accounts']:

                originBalance = user['balance'] // 100
                card_balance=originBalance
                card_number=user['maskedPan'][0]
                card_ids.append(user['id'])
                temp = user['maskedPan'][0]
                type = user['type']
                if temp[0] == '4':
                    card_type='Visa'
                elif temp[0] == '5':
                    card_type = 'Master'
                card_info=[]
                card_info.append({'number': card_number, 'balance': card_balance,'color': type, 'type': card_type})
                cards.append(card_info)
            #відображення витрат
            for user_id in card_ids:
                client1 = mono.get_statements(user_id, date(2024, 4, 4), date(2024, 4, 5))
                for payment in client1:
                    timeOrigin = datetime.fromtimestamp(payment['time'], timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    originAmount = payment['amount'] // 100
                    print(originAmount)
                    originAmounts.append(originAmount)
                    all_payments = []
                    payments.append({'time': timeOrigin, 'amount': originAmount, 'currency': payment['currencyCode'], 'category': payment['description']})
                    all_payments.append(payments)
                    labels.append(payment['description'])
                    data.append(originAmount)

            if not Card.objects.filter(card_number=card_number).exists():
                card_obj = Card(id=card_ids,balance=card_balance, card_number=card_number, token=token)
                card_obj.save()

        context = {'cards': cards, 'expenses':all_payments, 'labels': labels, 'data': data}
        return render(request, 'main/main_page.html', context)

    except monobank.Error as e:
             #сторінка для помилки ту мач реквест
        print("Помилка у функції get_cards:", e)
        return render(request, 'main/main_new.html')

def statistics_page(request):
    return render(request, 'main/statistic_page.html')
