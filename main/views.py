import monobank
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from monobank import Client
from datetime import datetime, date, timezone
import time
from .models import Card



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

def add_card(request):
    token = request.POST.get('token')
    labels = []
    data = []
    try:
        cards = []
        client = Client(token)
        user_info = client.get_client_info()
        request.session['token'] = token
        #додавання карти
        if user_info:
            for user in user_info['accounts']:
                originBalance = user['balance'] // 100
                card_balance=originBalance
                card_number=user['maskedPan'][0]
                card_id = user['id']
                temp = user['maskedPan'][0]
                type = user['type']
                if temp[0] == '4':
                    card_type='Visa'
                elif temp[0] == '5':
                    card_type = 'Master'
                card_info=[]
                card_info.append({'number': card_number, 'id': card_id, 'balance': card_balance,'color': type, 'type': card_type})
                cards.append(card_info)
            #відображення витрат
            if not Card.objects.filter(card_number=card_number).exists():
                card_obj = Card(id=card_id, balance=card_balance, card_number=card_number, token=token)
                card_obj.save()

        context = {'cards': cards, 'labels': labels, 'data': data}
        return render(request, 'main/main_page.html', context)

    except monobank.Error as e:
        # сторінка для помилки ту мач реквест
        print("Помилка у функції get_cards:", e)
        return render(request, 'main/main_new.html')

def get_payments(request, card_id):
    try:
        token = request.session.get('token')
        mono = monobank.Client(token)

        originAmounts = []
        payments = []

        statements = mono.get_statements(card_id, date(2024, 4, 5), date(2024, 4, 9))

        for statement in statements:
            timeOrigin = datetime.fromtimestamp(statement['time'], timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            originAmount = statement['amount'] // 100
            originAmounts.append(originAmount)

            payments.append({
                'time': timeOrigin,
                'amount': originAmount,
                'currency': statement['currencyCode'],
                'category': statement['description']
            })

        context = {'expences': payments, }
        return render(request, 'main/main_page.html', context)

    except Exception as e:
        print("Error in get_payments function:", e)
        return render(request, 'main/statistic_page.html')

def statistics_page(request):
    return render(request, 'main/statistic_page.html')
