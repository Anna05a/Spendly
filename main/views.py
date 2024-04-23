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

def caesar_cipher_encrypt(text, shift):
    encrypted_text = ''
    for char in text:
        if char.isalpha():
            shifted = ord(char) + shift
            if char.islower():
                if shifted > ord('z'):
                    shifted -= 26
                elif shifted < ord('a'):
                    shifted += 26
            elif char.isupper():
                if shifted > ord('Z'):
                    shifted -= 26
                elif shifted < ord('A'):
                    shifted += 26
            encrypted_text += chr(shifted)
        else:
            encrypted_text += char
    return encrypted_text

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
        card_ids=[]
        payments = []
        total_e=[]
        total_r=[]

        current_datetime = datetime.now()
        end_year = current_datetime.year
        end_month = current_datetime.month
        end_day = current_datetime.day

        one_month_ago = current_datetime - timedelta(days=30)
        start_year = one_month_ago.year
        start_month = one_month_ago.month
        start_day = one_month_ago.day
        statements = mono.get_statements(request.session['card_id'], date(start_year, start_month, start_day),
                                         date(end_year, end_month, end_day))

        for payment in statements:
            border=''
            img=''
            original_time = datetime.fromtimestamp(payment['time'], timezone.utc)
            new_time_str = (original_time + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
            originAmount = payment['amount'] // 100
            card_id = payment['id']
            # Зашифруємо айді карти методом Цезаря зі зсувом 3
            encrypted_card_id = caesar_cipher_encrypt(card_id, 3)

            card_ids.append(encrypted_card_id)

            # Додаємо card_id лише один раз до списку card_ids
            if card_id not in card_ids:
                card_ids.append(card_id)

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
                    total_e.append(abs(originAmount))
                else:
                    category = 'Enrollment'
                    total_e.append(originAmount)

            if category == 'Transfer':
                border = 'rgba(15, 110, 198, 1)'
                img = 'img/transfer.svg'
            elif category == 'Enrollment':
                border = 'rgba(135, 16, 176, 1)'
                img = 'img/lets-icons--transfer-down-light.png'
            elif category == 'Utility payments':
                border = 'rgba(180, 16, 16, 1)'
                img = "{ % static'img/utility.svg' %}"
            elif category == 'Transportation':
                border = 'rgba(213, 229, 25, 1)'
                img = 'img/transportation.svg'
            elif category == 'Health and beauty':
                border = 'rgba(233, 54, 183, 1)'
                img = 'img/health-and-beauty-outline.svg'
            elif category == 'Groceries':
                border = 'rgba(16, 176, 80, 1)'
                img = 'img/groceries.svg'
            elif category == 'Caffe/restaurant':
                border = 'rgba(100, 13, 141, 1)'
                img = 'img/cafe.svg'
            elif category == 'Services':
                border = 'rgba(57, 17, 171, 1)'
                img = 'img/services.svg'
            elif category == 'Entertainment':
                border = 'rgba(170, 16, 173, 1)'
                img = 'img/entertainment.svg'
            elif category == 'Travel':
                border = 'rgba(132, 193, 3, 1)'
                img = 'img/travel.svg'
            elif category == 'Household':
                border = 'rgba(176, 141, 16, 1)'
                img = 'img/household.svg'
            elif category == 'Car service':
                border = 'rgba(12, 204, 170, 1)'
                img = 'img/car-service.svg'
            elif category == 'Education':
                border = 'rgba(243, 220, 12, 1)'
                img = 'img/education.svg'
            elif category == 'Mobile recharge':
                border = 'rgba(17, 198, 210, 1)'
                img = 'img/mobile.svg'
            elif category == 'Other':
                border = 'rgba(214, 115, 24, 1)'
                img = 'img/other.svg'
            elif category == 'Shopping':
                border = 'rgba(0, 115, 46, 1)'
                img = 'img/shopping.svg'

            payments.append({
                'id': id,
                'time': new_time_str,
                'amount': originAmount,
                'currency': currency,
                'category': category,
                'description': payment['description'],
                'border': border,
                'img':img
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
        total_spending = []
        total_payments = []


        for payment in payments:
            category = payment['category']
            amount = payment['amount']
            currency = payment['currency']
            description = payment['description']
            time = payment['time']
            border1 = payment['border']
            img= payment['img']
            category_exists = False
            for item in total_spending:
                if item['category'] == category:
                    item['data'].append({
                        'amount': amount,
                        'border': border1,
                        'img': img,
                        'currency': currency,
                        'description': description,
                        'time': time
                    })
                    item['amount'] += amount
                    category_exists = True
                    break

            if not category_exists:
                total_spending.append({
                    'category': category,
                    'border': border1,
                    'img': img,
                    'amount': amount,
                    'data': [{
                        'amount': amount,
                        'currency': currency,
                        'description': description,
                        'time': time
                    }]
                })

            #print(total_spending)
            print(payment)
            #print(total_payments)
        context = { 'finances': finances, 'data': data, 'expence_persent': expence_percent, 'revenue_persent': revenue_percent, 'expences': total_spending, 'payments': total_payments,'revenue_data':total_r,'expense_data':total_e}
        return render(request, 'main/statistic_page.html', context)

    except Exception as e:
        print("Помилка у функції get_category_earn_cost:", e)
        return redirect('statistics')
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

                # Зашифруємо айді карти методом Цезаря зі зсувом 3
                encrypted_card_id = caesar_cipher_encrypt(card_id, 3)
                
                card_ids.append(encrypted_card_id)
                print(encrypted_card_id)
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

                if not Card.objects.filter(card_id=encrypted_card_id).exists():  # Перевіряємо, чи ідентифікатор уже існує
                    card_obj = Card.objects.create(id=uuid.uuid4(), card_id=encrypted_card_id, balance=card_balance, card_number=card_number, user=user, token=token, type=type, system=card_type)

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
        img=''
        current_datetime = datetime.now()
        end_year = current_datetime.year
        end_month = current_datetime.month
        end_day = current_datetime.day

        one_month_ago = current_datetime - timedelta(days=30)
        start_year = one_month_ago.year
        start_month = one_month_ago.month
        start_day = one_month_ago.day
        print(card_id)

        # Дешифруємо айді карти, яке прийшло з URL
        decrypted_card_id = caesar_cipher_encrypt(card_id, -3)
        request.session['card_id'] = decrypted_card_id
        statements = mono.get_statements(decrypted_card_id, date(start_year, start_month, start_day), date(end_year, end_month, end_day))
        print(decrypted_card_id)
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
                border='rgba(15, 110, 198, 1)'
                img =  'img/transfer.svg'
            elif category == 'Enrollment':
                border='rgba(135, 16, 176, 1)'
                img = 'img/enrollment.svg'
            elif category == 'Utility payments':
                border='rgba(180, 16, 16, 1)'
                img = "{ % static'img/utility.svg' %}"
            elif category == 'Transportation':
                border='rgba(213, 229, 25, 1)'
                img='img/transportation.svg'
            elif category == 'Health and beauty':
                border='rgba(233, 54, 183, 1)'
                img ='img/health-and-beauty-outline.svg'
            elif category == 'Groceries':
                border='rgba(16, 176, 80, 1)'
                img = 'img/groceries.svg'
            elif category == 'Caffe/restaurant':
                border='rgba(100, 13, 141, 1)'
                img = 'img/cafe.svg'
            elif category == 'Services':
                border='rgba(57, 17, 171, 1)'
                img = 'img/services.svg'
            elif category == 'Entertainment':
                border='rgba(170, 16, 173, 1)'
                img = 'img/entertainment.svg'
            elif category == 'Travel':
                border='rgba(132, 193, 3, 1)'
                img = 'img/travel.svg'
            elif category == 'Household':
                border='rgba(176, 141, 16, 1)'
                img = 'img/household.svg'
            elif category == 'Car service':
                border='rgba(12, 204, 170, 1)'
                img = 'img/car-service.svg'
            elif category == 'Education':
                border='rgba(243, 220, 12, 1)'
                img = 'img/education.svg'
            elif category == 'Mobile recharge':
                border='rgba(17, 198, 210, 1)'
                img = 'img/mobile.svg'
            elif category == 'Other':
                border = 'rgba(214, 115, 24, 1)'
                img = 'img/other.svg'
            elif category == 'Shopping':
                border = 'rgba(0, 115, 46, 1)'
                img = 'img/shopping.svg'

            payments.append({
                'id': id,
                'time': new_time_str,
                'amount': originAmount,
                'currency': currency,
                'category': category,
                'description': payment['description'],
                'border': border,
                'img': img
            })
            labels.append(category)

            data.append(originAmount)
        context = {'expences': payments, 'cards': cards, 'labels': labels, 'data': data}
        return render(request, 'main/main_page.html', context)

    except Exception as e:
        print("Error in get_payments function:", e)
        return render(request, 'main/statistic_page.html')


def refresh_card(request):
    try:
        card = Card.objects.filter(user=request.user).first()
        token = card.token
        client = Client(token)
        user_info = client.get_client_info()
        if user_info:
            for user_account in user_info['accounts']:
                originBalance = user_account['balance'] // 100
                card_balance = originBalance
                card_number = user_account['maskedPan'][0]
                card_id = user_account['id']
                encrypted_card_id = caesar_cipher_encrypt(card_id, 3)  # Шифруємо ідентифікатор карти
                temp = user_account['maskedPan'][0]
                type = user_account['type']
                if temp[0] == '4':
                    card_type = 'Visa'
                elif temp[0] == '5':
                    card_type = 'Master'
                if not Card.objects.filter(card_id=encrypted_card_id).exists():  # Перевіряємо зашифрований ідентифікатор
                    card_obj = Card.objects.create(id=uuid.uuid4(), card_id=encrypted_card_id, balance=originBalance, card_number=card_number, user=request.user, token=token, type=type, system=card_type)

        return redirect('home_page')
    except monobank.Error as e:
            print("Помилка у функції refresh_card:", e)
            return render(request, 'main/token_error.html')
