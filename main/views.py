import time
import iso18245
import pandas as pd
import pytz
import monobank
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from monobank import Client
from datetime import datetime, date, timedelta
from django.utils import timezone
from .models import Card, Category
import uuid



def get_mcc_description(mcc):
    try:
        merchant_category = iso18245.get_mcc(mcc).usda_description
    except:
        merchant_category = None
    return merchant_category


def read_csv(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        return df
    except Exception as e:
        print("Помилка у функції read_csv:", e)
        return None


def find_category(df, mcc_description):
    if df is not None:
        mask = df['description'] == mcc_description
        if mask.any():
            return df[mask]['category'].values[0]
    return mcc_description


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


class HomeView(View):
    @staticmethod
    @login_required(login_url='/login')
    def get(request):
        if Card.objects.filter(user=request.user).exists():
            time.sleep(30)
            return redirect('home_page')
        return render(request, 'main/main_new.html')

class StatisticsView(View):
    @staticmethod
    @login_required(login_url='/login')
    def get(request):
        return render(request, 'main/statistic_new.html')

class StatisticsPageView(View):
    @staticmethod
    @login_required(login_url='/login')
    def get(request):
        try:
            card_id=request.session['card_id']
            card=Card.objects.filter(card_id=card_id).first()
            originAmounts = []
            data = []
            finances = []
            expences = 0
            revenues = 0
            start_date=request.GET.get('start_date')
            end_date=request.GET.get('end_date')

            if start_date!=None and end_date!=None:
                payments = Category.objects.filter(time__range=[start_date, end_date], user=request.user)
                print(start_date,end_date)
                print(payments)
                print()
            else:
                today = timezone.now()
                month_away = today - timedelta(days=30)
                print(today, month_away)
                payments = Category.objects.filter(time__range=[month_away,today], user=request.user)

            total_e = []
            total_r = []
            total_spending = []
            total_payments = []
            originA=[]

            for payment in payments:
                originAmount = payment.amount
                category = payment.category
                currency = payment.currency
                description = payment.payment_desc
                time = payment.time

                originA.append(originAmount)
                originAmounts=[float(amount) for amount in originA]

                #функціонал для перегляду деталей кожної з категорії
                amount = originAmount
                if amount < 0:
                    category_exists = False
                    for item in total_spending:
                        if item['category'] == category:
                            item['data'].append({
                                'amount': amount,
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
                            'amount': amount,
                            'data': [{
                                'amount': amount,
                                'currency': currency,
                                'description': description,
                                'time': time
                            }]
                        })
            total_spending.sort(key=lambda x: x['amount'])

            # дістаємо дані з кругової діаграми
            for originAmount in originAmounts:
                # print(originAmount)
                if str(originAmount).startswith('-'):
                    expences += abs(originAmount) #для рахування відсотків витрат
                    total_e.append(abs(originAmount))
                else:
                    revenues += originAmount #для рахування відсотків доходу
                    total_r.append(originAmount)
            if expences == 0:
                expence_percent = 0
                revenue_percent = 0
            else:
                expence_percent = abs(round((100 * expences) / (expences + revenues), 1))
                revenue_percent = round((100 * revenues) / (expences + revenues), 1)
            data.append(expences)
            data.append(revenues)

            context = {'finances': finances, 'data': data, 'expence_persent': expence_percent,'revenue_persent': revenue_percent,
                       'expences': total_spending,'payments': total_payments,'revenue_data': total_r, 'expense_data': total_e, 'card_number':card}
            return render(request, 'main/statistic_page.html', context)
        except Exception as e:
            print(e)
            return redirect('statistics')
    @staticmethod
    def post(request):
        return redirect('statistics_page')


class HomePageView(View):
    @staticmethod
    @login_required(login_url='/login')
    def get(request):
        cards = Card.objects.filter(user=request.user)
        return render(request, 'main/main_page.html', {'cards': cards, 'user': request.user})

class AddCardView(View):
    @staticmethod
    @login_required(login_url='/login')
    def post(request):
        token = request.POST.get('token')
        card_ids = []
        try:

            client = Client(token)
            user_info = client.get_client_info()
            request.session['token'] = token
            print(user_info)
            if user_info:
                for user_account in user_info['accounts']:
                    originBalance = user_account['balance'] // 100
                    card_balance = originBalance
                    card_number = user_account['maskedPan'][0]
                    card_id = user_account['id']
                    card_type = user_account['type']
                    card_ids.append(card_id)
                    system=user_account['maskedPan'][0]
                    encrypted_card_id = caesar_cipher_encrypt(card_id, 3)

                    card_ids.append(encrypted_card_id)
                    print(encrypted_card_id)
                    temp = user_account['maskedPan'][0]
                    type = user_account['type']
                    if temp[0] == '4':
                        card_type = 'Visa'
                    elif temp[0] == '5':
                        card_type = 'Master'
                    print(card_ids)
                    if not Card.objects.filter(card_id=encrypted_card_id).exists():
                        Card.objects.create(id=uuid.uuid4(), card_id=encrypted_card_id, balance=card_balance,
                                                       card_number=card_number, user=request.user, token=token, type=card_type)

            return redirect('home_page')

        except monobank.Error as e:
            print("Помилка у функції get_cards:", e)
            return render(request, 'main/token_error.html')

class DeleteCardView(View):
    @staticmethod
    @login_required(login_url='/login')
    def get(request, card_id):
        card = Card.objects.filter(card_id=card_id)
        payments = Category.objects.filter(card_id=card_id)
        payments.delete()
        card.delete()
        if not card.exists():
            return redirect('home')
        else:
            return redirect('home_page')

class ClearCardsView(View):
    @staticmethod
    @login_required(login_url='/login')
    def get(request):
        cards = Card.objects.filter(user=request.user)
        cards.delete()
        payments= Category.objects.filter(user=request.user)
        payments.delete()
        return redirect('home')


class GetPaymentsView(View):
    @staticmethod
    @login_required(login_url='/login')
    def get(request, card_id):
        try:
            sv = request.GET.get('selected_value')
            print(sv)
            cards = Card.objects.filter(user=request.user, card_id=card_id)
            mono = monobank.Client(cards.first().token)
            originAmounts = []
            payments = []

            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            category_expenses ={}
            decrypted_card_id = caesar_cipher_encrypt(card_id, -3)
            request.session['card_id'] = card_id
            if start_date == None and end_date == None:
                current_datetime = datetime.now()
                end_year = current_datetime.year
                end_month = current_datetime.month
                end_day = current_datetime.day

                one_month_ago = current_datetime - timedelta(days=30)
                start_year = one_month_ago.year
                start_month = one_month_ago.month
                start_day = one_month_ago.day

                print(start_date)


                #print(decrypted_card_id)
                statements = mono.get_statements(decrypted_card_id, date(start_year, start_month, start_day),
                                                 date(end_year, end_month, end_day))
                for payment in statements:
                    original_time = datetime.fromtimestamp(payment['time'],  pytz.utc)
                    output_date_string = original_time.strftime("%Y.%m.%d")
                    new_time_str = (original_time + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
                    originAmount = payment['amount'] // 100
                    #
                    description=payment['description']
                    payment_id = payment['id']
                    pa=[]
                    pa.append(payment_id)
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
                        border = 'rgba(15, 110, 198, 1)'
                        img = 'img/transfer.svg'
                    elif category == 'Enrollment':
                        border = 'rgba(135, 16, 176, 1)'
                        img = 'img/enrollment.svg'
                    elif category == 'Utility payments':
                        border = 'rgba(180, 16, 16, 1)'
                        img = 'img/utility.svg'
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
                        'id': payment_id,
                        'time': new_time_str,
                        'amount': originAmount,
                        'currency': currency,
                        'category': category,
                        'description': description,

                    })
                    if category in category_expenses:
                            # Якщо так, додати суму витрат до існуючого значення
                        category_expenses[category] += originAmount
                    else:
                            # Якщо ні, створити новий запис з відповідною сумою витрат
                        category_expenses[category] = originAmount
                    labels = list(category_expenses.keys())
                    data = list(category_expenses.values())
                    if not Category.objects.filter(payment_id=payment_id).exists():
                        Category.objects.create(card_id=decrypted_card_id, payment_id=payment_id, payment_desc=payment['description'], user=request.user, time=new_time_str, amount=originAmount, currency=currency, category=category)
            else:
                statements = Category.objects.filter(time__range=[start_date, end_date], user=request.user)
                print(statements)
                for payment in statements:
                    originAmount=payment.amount
                    category = payment.category
                    payment_id = payment.payment_id
                    new_time_str = payment.time
                    currency = payment.currency
                    description = payment.payment_desc

                    payments.append({
                        'id': payment_id,
                        'time': new_time_str,
                        'amount': originAmount,
                        'currency': currency,
                        'category': category,
                        'description': description,

                    })


                    if category in category_expenses:
                            # Якщо так, додати суму витрат до існуючого значення
                        category_expenses[category] += originAmount
                    else:
                            # Якщо ні, створити новий запис з відповідною сумою витрат
                        category_expenses[category] = originAmount
                    labels = list(category_expenses.keys())
                    #data = list(category_expenses.values())
                    category_expenses_int = {key: int(value) for key, value in category_expenses.items()}
                    data=list(category_expenses_int.values())
                    print(labels, data)
            context = {'id':card_id,'expences': payments, 'cards': cards, 'labels': labels, 'data': data}
            return render(request, 'main/main_page.html', context)

        except Exception as e:
            print(f"API request error: {e}")
            return render(request, 'main/too_many_requests.html')

    def post(self, request, card_id):
        try:

            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            print(start_date, end_date)
            return self.get(request, card_id)
        except Exception as e:
            print(e)


def refresh(request):
    try:
        card = Card.objects.filter(user=request.user).first()
        client = monobank.Client(card.token)
        user_info = client.get_client_info()
        user=request.user
        if user_info:
            for user_account in user_info['accounts']:
                originBalance = user_account['balance'] // 100
                card_balance = originBalance
                card_number = user_account['maskedPan'][0]
                card_id = user_account['id']
                encrypted_card_id = caesar_cipher_encrypt(card_id, 3)

                temp = user_account['maskedPan'][0]
                type = user_account['type']
                if temp[0] == '4':
                    card_type = 'Visa'
                elif temp[0] == '5':
                    card_type = 'Master'
                if not Card.objects.filter(user=user, card_id=encrypted_card_id).exists():
                    # Перевіряємо зашифрований ідентифікатор
                    Card.objects.create(id=uuid.uuid4(), card_id=card_id, balance=card_balance,
                                        card_number=card_number, user=request.user, token=card.token, type=type,
                                        system=card_type)
                else:
                    Card.objects.filter(user=user, card_id=encrypted_card_id).update(balance=card_balance)

        return redirect('home_page')
    except Exception as e:
        print("Помилка у функції refresh_card:", e)
        return render(request, 'main/too_many_requests.html')