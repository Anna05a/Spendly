from django import forms
import monobank
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from monobank import Client
from datetime import datetime, date, timezone, timedelta
import time

from API.views import get_mcc_description, find_category, read_csv
from .models import Card
import uuid


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
    cards = Card.objects.filter(user=request.user)
    return render(request, 'main/main_page.html', {'cards': cards, 'user': request.user})


def add_card(request):
    token = request.POST.get('token')

    card_ids=[]
    try:
        cards = []
        client = Client(token)
        user_info = client.get_client_info()
        request.session['token'] = token
        # Отримання поточного користувача
        user = request.user
        print(user_info)
        # додавання карти
        if user_info:
            for user_account in user_info['accounts']:
                originBalance = user_account['balance'] // 100
                card_balance = originBalance
                card_number = user_account['maskedPan'][0]
                card_id = user_account['id']
                card_ids.append(card_id)

                # Додаємо card_id лише один раз до списку card_ids
                if card_id not in card_ids:
                    card_ids.append(card_id)

                temp = user_account['maskedPan'][0]
                type = user_account['type']
                if temp[0] == '4':
                    card_type = 'Visa'
                elif temp[0] == '5':
                    card_type = 'Master'
                print(card_ids)
                card_info = []
                card_info.append({'number': card_number, 'id': card_id, 'balance': card_balance,'color': type, 'type': card_type})
                cards.append(card_info)
            # відображення витрат
                if not Card.objects.filter(card_id=card_id).exists():  # Перевіряємо, чи ідентифікатор уже існує
                    card_obj = Card.objects.create(id=uuid.uuid4(), card_id=card_id, balance=card_balance, card_number=card_number, user=user, token=token, type=type, system=card_type)

        context = {'cards': cards}
        return redirect('home_page')

    except monobank.Error as e:
        # сторінка для помилки ту мач реквест
        print("Помилка у функції get_cards:", e)
        return render(request, 'main/token_error.html')


def get_payments(request, card_id):
    try:
        cards = Card.objects.filter(user=request.user)
        mono = monobank.Client(cards.first().token)
        labels = []
        data = []
        originAmounts = []
        payments = []

        statements = mono.get_statements(card_id, date(2024, 4, 5), date(2024, 4, 9))

        for payment in statements:
            original_time = datetime.fromtimestamp(payment['time'], timezone.utc)
            new_time_str = (original_time + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
            originAmount = payment['amount'] // 100
            originAmounts.append(originAmount)
            currency = ''
            if payment['currencyCode'] == 980:
                currency = 'UAH'
            if payment['currencyCode'] == 840:
                currency = 'USD'
            if payment['currencyCode'] == 978:
                currency = 'EUR'
            mcc_descriptionTemp = get_mcc_description(str(payment.get('mcc', '')))
            mcc_description = mcc_descriptionTemp.lower().replace('â€“', '')
            if payment['mcc'] == 7832:
                mcc_description = 'motion picture theatres'
            # print('mcc', payment['mcc'])
            # print('TTTT',mcc_description )
            df = read_csv('category.csv')
            category = find_category(df, mcc_description)
            if category.lower() == 'фінанси':
                if str(originAmount).startswith('-'):
                    category = 'переказ'
                else:
                    category = 'зарахування'


            payments.append({
                'time': new_time_str,
                'amount': originAmount,
                'currency': currency,
                'category': category,
                'description': payment['description']
            })
            labels.append(category)
            data.append(originAmount)
        context = {'expences': payments, 'cards': cards, 'labels': labels, 'data': data}
        return render(request, 'main/main_page.html', context)

    except Exception as e:
        print("Error in get_payments function:", e)
        return render(request, 'main/statistic_page.html')
