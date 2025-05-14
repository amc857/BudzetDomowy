import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from budzetApp.models import Budget, BudgetTransaction, Category, Transaction, UserBudget, User, Uzytkownicy
from django.contrib import messages
from .forms import BudgetForm, UserRegistrationForm
from django.urls import reverse_lazy

from django.db.models import Sum
from django.core.paginator import Paginator
from budzetApp.models import Transaction, Category
from budzetApp.forms import TransactionForm


from .models import Budzety, UzytkownikBudzetPolaczenia, Kategorie, Transakcje, Uzytkownicy

# Create your views here.

def login(request):
    
    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')



        # Sprawdzenie, czy użytkownik istnieje w bazie danych
        user = Uzytkownicy.objects.filter(username=username, email=email, password=password)
        if user.exists():

            request.session['user_id'] = user.first().id 

            return redirect('budzetApp:index')
        else:
            # Użytkownik nie istnieje
            messages.error(request, "Nie znaleziono użytkownika o podanych danych.")
            return redirect('budzetApp:login')
        
    return render(request, 'budzetApp/login.html')

def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save()
            
            return redirect('budzetApp:budget_list')
    else:
        form = BudgetForm()
        transactions = Transakcje.objects.filter(user_id=request.session['user_id'])  # Transakcje użytkownika
    return render(request, 'budzetApp/create_budget.html', {'form': form})

def budget_list(request):
    budgets = Budzety.objects.all()
    budget_summaries = []

    for budget in budgets:
        transactions = Transakcje.objects.select_related('budget').filter(budget=budget.id)
        total_transactions = sum(bt.amount for bt in transactions)
        budget_summaries.append({
            'budget': budget,
            'transactions': transactions,
            'total_transactions': total_transactions,
            'remaining': budget.budget_amount - total_transactions
        })

def register(request):  #BYŁĄ ZMIANA BAZY DANYCH, DOSTOSOWAĆ DO NOWEJ
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
           
            user = form.save(commit=False)
            user.password = form.cleaned_data['password'] 
            user.save()
            messages.success(request, "Rejestracja zakończona sukcesem! Możesz się teraz zalogować.")
            return redirect('budzetApp:login') 
    else:
        form = UserRegistrationForm()
    return render(request, 'budzetApp/register.html', {'form': form})


#-----------------------------------------------------------
def index(request):
    transaction_list = Transaction.objects.all().order_by('-transaction_date')

    paginator = Paginator(transaction_list, 10)
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)
    

    total_income = Transaction.objects.filter(
        amount__gt=0
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_expenses = Transaction.objects.filter(
        amount__lt=0
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'is_paginated': transactions.has_other_pages(),
        'page_obj': transactions,
    }
    
    return render(request, 'budzetApp/index.html', context)

def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            if request.user.is_authenticated:
                transaction.user = request.user
            transaction.save()
            return redirect('budzetApp:index')
    else:
        form = TransactionForm()
    
    context = {
        'form': form,
        'transaction': None,
        'categories': Category.objects.all()
    }
    return render(request, 'budzetApp/addtransaction.html', context)

def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('budzetApp:index')
    else:
        form = TransactionForm(instance=transaction)
    
    context = {
        'form': form,
        'transaction': transaction,
        'categories': Category.objects.all()
    }
    return render(request, 'budzetApp/addtransaction.html', context)


def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        return redirect('budzetApp:index')
    
    context = {
        'object': transaction
    }
    return render(request, 'budzetApp/confirm_delete.html', context)


def transaction_list(request):
    if request.session.get('username'):
        transactions = Transaction.objects.filter(user__id=request.session['user_id']).order_by('-transaction_date')
        return render(request, 'budzetApp/transaction.html', {'transactions': transactions})
    return redirect('budzetApp:index')

