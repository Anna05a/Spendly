from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url='/login')
def home(request):
    return render(request,'finances/main_new.html')

def statistics(request):
    return render(request, 'finances/statistic_new.html')