from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from API.views import get_pay, get_cards
# Create your views here.

@login_required(login_url='/login')
def home(request):
    return render(request,'finances/main_new.html')

def statistics(request):
    return render(request, 'finances/statistic_new.html')

@login_required(login_url='/login')
def statistics_page(request):
    return render(request, 'finances/statistic_page.html')

@login_required(login_url='/login')
def home_page(request):
    return render(request, 'finances/main_page.html')

def get_token(request):
    pass
    return render(request, 'finances/get_token.html')
def add_card(request):
    if request.method == 'POST':
        user = request.user
        token=request.POST['token']
        try:
            card_data = get_cards(token)
            if card_data:
                for card in card_data:
                    card_id = card['card_id']  # ID картки
                    card_type = card['card_type']  # Тип картки
                    card_number = card['card_number']  # Номер картки
                    card_balance = card['card_balance']  # Баланс картки
            context = { 'balance': card_balance, 'number': card_number}
            return render(request, 'finances/main_page.html', context)
        except Exception as e:
            print("Error in add_card:", e)
            return render(request, 'finances/main_page.html', {'error': 'Error fetching cards'})
