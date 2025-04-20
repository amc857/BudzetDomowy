from django.shortcuts import render
from django.http import HttpResponseRedirect

#from .forms import UserLoginForm, FoodForm
#from .models import User, Food


# Create your views here.

def index(request):
    return render(request,"budzetApp/index.html")


def login(request):
    return render(request, 'budzetApp/login.html')