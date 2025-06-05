import re
from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from budzetApp.models import Budget, BudgetTransaction, Category, Transaction, UserBudget, User, Uzytkownicy
from django.contrib import messages
from .forms import AddUserToBudgetForm, BudgetForm, KategorieCreateForm, UserRegistrationForm
from django.urls import reverse_lazy

from django.db.models import Sum
from django.core.paginator import Paginator
from budzetApp.models import Transaction, Category

from .forms import TransakcjeForm
from .models import BudgetInvitation, Budzety, UzytkownikBudzetPolaczenia, Kategorie, Transakcje, Uzytkownicy

import secrets
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

def login(request):
    
    if request.method == 'POST':

        username = request.POST.get('username')
        #email = request.POST.get('email')
        password = request.POST.get('password')



        # Sprawdzenie, czy użytkownik istnieje w bazie danych
        user = Uzytkownicy.objects.filter(username=username, password=password)
        if user.exists():

            request.session['user_id'] = user.first().id 

            return redirect('budzetApp:index')
        else:
            # Użytkownik nie istnieje
            messages.error(request, "Nie znaleziono użytkownika o podanych danych.")
            return redirect('budzetApp:login')
        
    return render(request, 'budzetApp/login.html')

def create_budget(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Musisz być zalogowany, aby utworzyć budżet.")
        return redirect('budzetApp:login')

    user = Uzytkownicy.objects.get(pk=user_id)

    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.save()
            budget.users.set([user])  # Przypisz tylko aktualnego użytkownika
            # Tworzenie 3 podstawowych kategorii
            Kategorie.objects.create(category_name="Codzienne wydatki", budget=budget)
            Kategorie.objects.create(category_name="Osobiste", budget=budget)
            Kategorie.objects.create(category_name="Subskrypcje", budget=budget)
            return redirect('budzetApp:budget_list')
    else:
        form = BudgetForm()
    return render(request, 'budzetApp/create_budget.html', {'form': form})

def budget_list(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('budzetApp:login')

    user = Uzytkownicy.objects.get(pk=user_id)
    budgets = Budzety.objects.filter(users=user)
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

    return render(request, 'budzetApp/budget_list.html', {'budget_summaries': budget_summaries})

    return render(request, 'budzetApp/budget_list.html', {'budget_summaries': budget_summaries})
def register(request):
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
    user = None
    user_id = request.session.get('user_id')
    if user_id:
        user = Uzytkownicy.objects.get(pk=user_id)

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
        'current_user': user,
    }

    return render(request, 'budzetApp/index.html', context)

def add_transaction(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Musisz być zalogowany, aby dodać transakcję.")
        return redirect('budzetApp:login')

    user = Uzytkownicy.objects.get(pk=user_id)
    # Budżety utworzone przez użytkownika lub do których ma dostęp
    budgets_qs = Budzety.objects.filter(users=user).distinct()

    if request.method == 'POST':
        form = TransakcjeForm(request.POST, budgets_qs=budgets_qs)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = user
            transaction.save()
            return redirect('budzetApp:budget_list')
    else:
        form = TransakcjeForm(budgets_qs=budgets_qs)
    return render(request, 'budzetApp/addtransaction.html', {'form': form})


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
    user_id = request.session['user_id']
    transactions = []
    if user_id:
        user = Uzytkownicy.objects.get(pk=user_id)
        transactions = Transakcje.objects.filter(user=user).order_by('-transaction_date')
    context = {
        'transactions': transactions
    }
    return render(request, 'budzetApp/transaction.html', context)

def create_category(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Musisz być zalogowany, aby dodać kategorię.")
        return redirect('budzetApp:login')

    user = Uzytkownicy.objects.get(pk=user_id)
    user_budgets = Budzety.objects.filter(users=user)
    if request.method == 'POST':
        form = KategorieCreateForm(request.POST, budgets_qs=user_budgets)
        if form.is_valid():
            form.save()
            return redirect('budzetApp:budget_list')
    else:
        form = KategorieCreateForm(budgets_qs=user_budgets)
    return render(request, 'budzetApp/create_category.html', {'form': form})

def add_user_to_budget(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Musisz być zalogowany.")
        return redirect('budzetApp:login')

    user = Uzytkownicy.objects.get(pk=user_id)
    user_budgets = Budzety.objects.filter(users=user)

    selected_budget = None
    current_users = []
    if request.method == 'POST':
        budget_id = request.POST.get('budget')
        if budget_id:
            selected_budget = Budzety.objects.get(pk=budget_id)
            current_users = selected_budget.users.all()
        form = AddUserToBudgetForm(request.POST, budgets_qs=user_budgets, selected_budget=selected_budget)
        if form.is_valid():
            selected_user = form.cleaned_data['user']
            selected_budget = form.cleaned_data['budget']
            selected_budget.users.add(selected_user)
            messages.success(request, f"Użytkownik {selected_user.username} został dodany do budżetu {selected_budget.name}.")
            return redirect('budzetApp:add_user_to_budget')  # Odśwież, by zobaczyć aktualną listę
    else:
        form = AddUserToBudgetForm(budgets_qs=user_budgets)
        # Jeśli GET z parametrem budget, pokaż obecnych użytkowników
        budget_id = request.GET.get('budget')
        if budget_id:
            try:
                selected_budget = Budzety.objects.get(pk=budget_id)
                current_users = selected_budget.users.all()
                form = AddUserToBudgetForm(budgets_qs=user_budgets, selected_budget=selected_budget)
            except Budzety.DoesNotExist:
                pass

    return render(request, 'budzetApp/add_user_to_budget.html', {
        'form': form,
        'current_users': current_users,
        'selected_budget': selected_budget,
    })

def get_budget_users(request):
    budget_id = request.GET.get('budget_id')
    users_list = []
    if budget_id:
        try:
            budget = Budzety.objects.get(pk=budget_id)
            users = budget.users.all()
            users_list = [{'username': u.username} for u in users]
        except Budzety.DoesNotExist:
            pass
    return JsonResponse({'users': users_list})


def logout_view(request):
    request.session.flush()
    return render(request, 'budzetApp/logout.html')

def edit_profile(request):
    user_id = request.session.get('user_id')
    current_user = None
    if user_id:
        current_user = Uzytkownicy.objects.get(pk=user_id)
    # ...obsługa POST i walidacja...
    return render(request, 'budzetApp/edit_profile.html', {'current_user': current_user})



def add_user_to_budget(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Musisz być zalogowany.")
        return redirect('budzetApp:login')

    user = Uzytkownicy.objects.get(pk=user_id)
    user_budgets = Budzety.objects.filter(users=user)

    selected_budget = None
    current_users = []
    if request.method == 'POST':
        budget_id = request.POST.get('budget')
        if budget_id:
            selected_budget = Budzety.objects.get(pk=budget_id)
            current_users = selected_budget.users.all()
        form = AddUserToBudgetForm(request.POST, budgets_qs=user_budgets, selected_budget=selected_budget)
        if form.is_valid():
            selected_user = form.cleaned_data['user']
            selected_budget = form.cleaned_data['budget']

            # Generowanie tokena i zapis zaproszenia
            token = secrets.token_urlsafe(32)
            invitation = BudgetInvitation.objects.create(
                invited_user=selected_user,
                budget=selected_budget,
                token=token
            )

            # Wysyłka e-maila z linkiem
            invite_link = request.build_absolute_uri(
                f"/accept_invitation/?token={token}"
            )
            send_mail(
                subject="Zaproszenie do budżetu",
                message=f"Otrzymałeś zaproszenie do budżetu '{selected_budget.name}'. Kliknij, aby dołączyć: {invite_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[selected_user.email],
                fail_silently=True,
            )

            messages.success(request, f"Zaproszenie zostało wysłane do {selected_user.username} ({selected_user.email}).")
            return redirect('budzetApp:add_user_to_budget')
    else:
        form = AddUserToBudgetForm(budgets_qs=user_budgets)
        budget_id = request.GET.get('budget')
        if budget_id:
            try:
                selected_budget = Budzety.objects.get(pk=budget_id)
                current_users = selected_budget.users.all()
                form = AddUserToBudgetForm(budgets_qs=user_budgets, selected_budget=selected_budget)
            except Budzety.DoesNotExist:
                pass

    return render(request, 'budzetApp/add_user_to_budget.html', {
        'form': form,
        'current_users': current_users,
        'selected_budget': selected_budget,
    })

def accept_invitation(request):
    token = request.GET.get('token')
    invitation = get_object_or_404(BudgetInvitation, token=token, accepted=False)
    user = invitation.invited_user
    budget = invitation.budget

    # Dodaj użytkownika do budżetu
    budget.users.add(user)
    invitation.accepted = True
    invitation.save()
    messages.success(request, f"Dołączyłeś do budżetu {budget.name}.")
    return redirect('budzetApp:budget_list')

def get_budget_categories(request):
    budget_id = request.GET.get('budget_id')
    categories = []
    if budget_id:
        categories = Kategorie.objects.filter(budget_id=budget_id)
    data = [{'id': c.id, 'name': c.category_name} for c in categories]
    return JsonResponse({'categories': data})