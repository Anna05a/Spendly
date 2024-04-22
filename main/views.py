from django import forms
import monobank
from django.http import JsonResponse
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
    if Card.objects.filter(user=request.user).exists():
        return redirect('home_page')
    return render(request,'main/main_new.html')
@login_required(login_url='/login')
def statistics(request):
    return render(request, 'main/statistic_new.html')

@login_required(login_url='/login')
def statistics_page(request):
    try:
        cards = Card.objects.filter(user=request.user)
        mono = monobank.Client(cards.first().token)
        originAmounts=[]
        data = []
        finances = []
        expences = 0
        revenues = 0
        count_e=0
        count_r=0

        payments = []


        statements = mono.get_statements(request.session['card_id'], date(2024, 3, 28),
                                         date(2024, 4, 20))
        for payment in statements:
            original_time = datetime.fromtimestamp(payment['time'], timezone.utc)
            new_time_str = (original_time + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
            originAmount = payment['amount'] // 100
            id = payment['id']
            originAmounts.append(originAmount)
            currency = ''
            if payment['currencyCode'] == 980:
                currency = 'UAH'
            if payment['currencyCode'] == 840:
                currency = 'USD'
            if payment['currencyCode'] == 978:
                currency = 'EUR'
            mcc_descriptionTemp = get_mcc_description(str(payment.get('mcc', '')))
            mcc_description = mcc_descriptionTemp.lower().replace('â€“', '').replace('вђ“', '')
            if payment['mcc'] == 7832:
                mcc_description = 'motion picture theatres'
            if payment['mcc'] == 4816:
                mcc_description = 'computer network/information services'
            if payment['mcc'] == 5816:
                mcc_description = 'digital goods – games'
            df = read_csv('category.csv')
            category = find_category(df, mcc_description)
            if category.lower() == 'finance':
                if str(originAmount).startswith('-'):
                    category = 'Transfer'
                else:
                    category = 'Enrollment'
            payments.append({
                'id': id,
                'time': new_time_str,
                'amount': originAmount,
                'currency': currency,
                'category': category,
                'description': payment['description'],
                #'border': border
            })
        for originAmount in originAmounts:
            if str(originAmount).startswith('-'):
                expences += abs(originAmount)
                count_e+=1
            else:
                revenues += originAmount
                count_r+=1
        revenue_percent = abs(round((100*expences)/(expences+revenues),1))
        expence_percent = round((100*revenues)/(expences+revenues),1)
        data.append(expences)
        data.append(revenues)
        total_spending = {}
        total_payments = {}

        for payment in payments:
            category = payment['category']
            amount = payment['amount']
            currency = payment['currency']
            description = payment['description']
            time = payment['time']
            if category not in total_spending:
                total_spending[category] = 0
            total_spending[category] += amount
            if category not in total_payments:
                total_payments[category] = []

            total_payments[category].append({
                'amount': amount,
                'currency': currency,
                'description': description,
                'time': time
            })
            print(payment)
            print(total_payments)
        context = { 'finances': finances, 'data': data, 'expence_persent': expence_percent, 'revenue_persent': revenue_percent, 'expences': total_spending, 'payments': total_payments}
        return render(request, 'main/statistic_page.html', context)

    except Exception as e:
        print("Помилка у функції get_category_earn_cost:", e)
        return render(request, 'main/main_new.html')
@login_required(login_url='/login')
def home_page(request):
    cards = Card.objects.filter(user=request.user)
    return render(request, 'main/main_page.html', {'cards': cards, 'user': request.user})


def add_card(request):
    token = request.POST.get('token')
    card_ids=[]
    try:
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

                if not Card.objects.filter(card_id=card_id).exists():  # Перевіряємо, чи ідентифікатор уже існує
                    card_obj = Card.objects.create(id=uuid.uuid4(), card_id=card_id, balance=card_balance, card_number=card_number, user=user, token=token, type=type, system=card_type)

        return redirect('home_page')

    except monobank.Error as e:
        # сторінка для помилки ту мач реквест
        print("Помилка у функції get_cards:", e)
        return render(request, 'main/token_error.html')


def delete_card(request, card_id):
    card = Card.objects.filter(card_id=card_id)
    card.delete()
    if not card.exists():
        return redirect('home')
    else:
        return redirect('home_page')


def get_payments(request, card_id):
    try:

        cards = Card.objects.filter(user=request.user)
        mono = monobank.Client(cards.first().token)
        labels = []
        data = []
        originAmounts = []
        payments = []
        border=''
        current_datetime = datetime.now()
        end_year = current_datetime.year
        end_month = current_datetime.month
        end_day = current_datetime.day

        one_month_ago = current_datetime - timedelta(days=30)
        start_year = one_month_ago.year
        start_month = one_month_ago.month
        start_day = one_month_ago.day

        statements = mono.get_statements(card_id, date(start_year, start_month, start_day), date(end_year, end_month, end_day))

        for payment in statements:
            original_time = datetime.fromtimestamp(payment['time'], timezone.utc)
            new_time_str = (original_time + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
            originAmount = payment['amount'] // 100
            id = payment['id']
            originAmounts.append(originAmount)
            request.session['originAmounts'] = originAmounts
            currency = ''
            if payment['currencyCode'] == 980:
                currency = 'UAH'
            if payment['currencyCode'] == 840:
                currency = 'USD'
            if payment['currencyCode'] == 978:
                currency = 'EUR'
            mcc_descriptionTemp = get_mcc_description(str(payment.get('mcc', '')))
            mcc_description = mcc_descriptionTemp.lower().replace('â€“', '').replace('вђ“', '')
            if payment['mcc'] == 7832:
                mcc_description = 'motion picture theatres'
            if payment['mcc'] == 4816:
                mcc_description = 'computer network/information services'
            if payment['mcc'] == 5816:
                mcc_description = 'digital goods – games'
            df = read_csv('category.csv')
            category = find_category(df, mcc_description)
            if category.lower() == 'finance':
                if str(originAmount).startswith('-'):
                    category = 'Transfer'
                else:
                    category = 'Enrollment'

            if category == 'Transfer':
                border=''
            elif category == 'Enrollment':
                border='rgba(135, 16, 176, 1)'
            elif category == 'Utility payments':
                border=''
            elif category == 'Transportation':
                border=''
                imq='<'
            elif category == 'Health and beauty':
                border=''
            elif category == 'Groceries':
                border=''
            elif category == 'Caffe/restaurant':
                border=''
            elif category == 'Services':
                border=''
            elif category == 'Entertainment':
                border=''
            elif category == 'Travel':
                border=''
            elif category == 'Household':
                border=''
            elif category == 'Car service':
                border=''
            elif category == 'Education':
                border=''
            elif category == 'Mobile recharge':
                border='rgba(17, 198, 210, 1)'

            payments.append({
                'id': id,
                'time': new_time_str,
                'amount': originAmount,
                'currency': currency,
                'category': category,
                'description': payment['description'],
                'border': border
            })
            labels.append(category)
            request.session['card_id'] = card_id
            data.append(originAmount)
        context = {'expences': payments, 'cards': cards, 'labels': labels, 'data': data}
        return render(request, 'main/main_page.html', context)

    except Exception as e:
        print("Error in get_payments function:", e)
        return render(request, 'main/statistic_page.html')


def refresh_card(request):
    try:
        card = Card.objects.filter(user=request.user).first()
        token=card.token
        client = Client(token)
        user_info = client.get_client_info()
        if user_info:
            for user_account in user_info['accounts']:
                originBalance = user_account['balance'] // 100
                card_id = user_account['id']
                temp = user_account['maskedPan'][0]
                if temp[0] == '4':
                    card_type = 'Visa'
                elif temp[0] == '5':
                    card_type = 'Master'
                if not Card.objects.filter(card_id=card_id).exists():  # Перевіряємо, чи ідентифікатор уже існує
                    Card.objects.create(id=uuid.uuid4(), card_id=card_id, balance=originBalance, card_number=originBalance,user=request.user, token=token, type=user_account['type'], system=card_type)
                else:
                    Card.objects.filter(user=request.user).update(balance=originBalance)

        return redirect('home_page')
    except monobank.Error as e:
            print("Помилка у функції refresh_card:", e)
            return render(request, 'main/token_error.html')