from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from API.views import get_pay, get_cards, token
from API.models import Card
# Create your views here.

@login_required(login_url='/login')
def home(request):
    return render(request, 'main/main_new.html')
@login_required(login_url='/login')
def statistics(request):
    return render(request, 'main/statistic_new.html')

@login_required(login_url='/login')
def statistics_page(request):
    return render(request, 'main/statistic_page.html')

@login_required(login_url='/login')
def home_page(request):
    return render(request, 'main/main_page.html')

#def get_token(request):
#    return render(request, 'main/get_token.html')

def add_card(request):
    if request.method == 'POST':
        try:
            token = request.POST.get('token')
            if token:
                card_data = get_cards()
                for card in card_data:
                    card_id = card['card_id']
                    card_number = card['card_number']
                    card_balance = card['card_balance']

                    # Сохранение данных о карте в базу данных
                    card_obj = Card.objects.create(id=card_id, balance=card_balance, card_number=card_number)

                context = {'cards': card_data}  # Передача данных в контекст для отображения в шаблоне
                return render(request, 'main/main_page.html', context)
            else:
                return render(request, 'main/statistic_new.html', {'error': 'Token is missing in request'})
        except Exception as e:
            print("Error in add_card:", e)
            return render(request, 'main/statistic_new.html', {'error': 'Error fetching cards'})