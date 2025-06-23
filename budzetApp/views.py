# Standard library
import secrets

# Django core
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Sum
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from urllib.parse import urlencode

# App models
from budzetApp.models import (
    Budzety, Uzytkownicy, Kategorie, Transakcje, UzytkownikBudzetPolaczenia,
    BudgetInvitation
)

# App forms
from .forms import (
    AddUserToBudgetForm, BudgetForm, KategorieCreateForm, UserRegistrationForm, TransakcjeForm
)

# Create your views here.

#----------------------------------------------------------------------

# Strona główna aplikacji budżetowej

# Main panel
def index(request):
    user = None
    user_id = request.session.get('user_id')
    budgets = []
    selected_budget = None
    total_income = 0
    total_expenses = 0
    transactions = []

    if user_id:
        user = Uzytkownicy.objects.get(pk=user_id)
        budgets = Budzety.objects.filter(users=user).order_by('id')
        selected_budget_id = request.GET.get('budget')
        if selected_budget_id:
            selected_budget = budgets.filter(id=selected_budget_id).first()
        else:
            selected_budget = budgets.first() if budgets.exists() else None

        if selected_budget:
            transactions = Transakcje.objects.filter(budget=selected_budget).order_by('-transaction_date')
            total_income = transactions.filter(amount__gt=0).aggregate(Sum('amount'))['amount__sum'] or 0
            total_expenses = transactions.filter(amount__lt=0).aggregate(Sum('amount'))['amount__sum'] or 0


    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    users_in_budget = []
    if selected_budget:
        transactions = Transakcje.objects.filter(budget=selected_budget).order_by('-transaction_date')
        total_income = transactions.filter(amount__gt=0).aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenses = transactions.filter(amount__lt=0).aggregate(Sum('amount'))['amount__sum'] or 0
        users_in_budget = selected_budget.users.all()

    context = {
        'budgets': budgets,
        'selected_budget': selected_budget,
        'current_user': user,
        'transactions': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'users_in_budget': users_in_budget,
    }

    return render(request, 'budzetApp/index.html', context)

#----------------------------------------------------------------------

# Zarządzanie użytkownikami

# Strona logowania
def login(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'budzetApp:index'

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = Uzytkownicy.objects.filter(username=username, password=password)
        if user.exists():
            request.session['user_id'] = user.first().id
            messages.info(request, f"Przeniesienie na {next_url}.")
            return redirect(next_url)
        else:
            messages.error(request, "Nie znaleziono użytkownika o podanych danych.")
            return render(request, 'budzetApp/login.html', {'next': next_url})

    return render(request, 'budzetApp/login.html', {'next': next_url})


# Strona rejestracji użytkownika
def register(request):
    next_url = request.GET.get('next') or request.POST.get('next') or None

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
           
            user = form.save(commit=False)
            user.password = form.cleaned_data['password'] 
            user.save()
            messages.success(request, "Rejestracja zakończona sukcesem! Możesz się teraz zalogować.")
            if next_url:
                login_url = f"{reverse_lazy('budzetApp:login')}?{urlencode({'next': next_url})}"
                return redirect(login_url)
            return redirect('budzetApp:login') 
        else:
            messages.error(request, "Rejestracja nie udana.")
            return render(request, 'budzetApp/register.html', {'form': form, 'next': next_url})
    else:
        form = UserRegistrationForm()
        
    return render(request, 'budzetApp/register.html', {'form': form, 'next': next_url})

# Strona wylogowania
def logout_view(request):
    request.session.flush()
    return render(request, 'budzetApp/logout.html')

# Strona edycji profilu użytkownika
def edit_profile(request):
    user_id = request.session.get('user_id')
    current_user = None
    if user_id:
        current_user = Uzytkownicy.objects.get(pk=user_id)
    # ...obsługa POST i walidacja...
    return render(request, 'budzetApp/edit_profile.html', {'current_user': current_user})

#----------------------------------------------------------------------

# Zarządzanie budżetami

# Strona tworzenia budżetu
def create_budget(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You need to be logged to create budget.")
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

# Strona listy budżetów
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
        users_in_budget = budget.users.all()
        budget_summaries.append({
            'budget': budget,
            'transactions': transactions,
            'total_transactions': total_transactions,
            'remaining': budget.budget_amount - total_transactions,
            'users': users_in_budget,
        })

    return render(request, 'budzetApp/budget_list.html', {'budget_summaries': budget_summaries})

    return render(request, 'budzetApp/budget_list.html', {'budget_summaries': budget_summaries})

# Strona dodawania użytkownika do budżetu
def add_user_to_budget(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Musisz być zalogowany.")
        return redirect('budzetApp:login')

    user = Uzytkownicy.objects.get(pk=user_id)
    user_budgets = Budzety.objects.filter(users=user)

    selected_budget = None
    current_users = []
    invite_link = None

    if request.method == 'POST':
        form = AddUserToBudgetForm(request.POST, budgets_qs=user_budgets)
        if form.is_valid():
            selected_budget = form.cleaned_data['budget']

            # Generowanie tokena i zapis zaproszenia (bez invited_user)
            token = secrets.token_urlsafe(32)
            invitation = BudgetInvitation.objects.create(
                budget=selected_budget,
                token=token
            )

            invite_link = request.build_absolute_uri(
                f"/accept_invitation/?token={token}"
            )
            messages.success(request, f"Skopiuj link i przekaż użytkownikowi: {invite_link}")
            current_users = selected_budget.users.all()
    else:
        form = AddUserToBudgetForm(budgets_qs=user_budgets)
        budget_id = request.GET.get('budget')
        if budget_id:
            try:
                selected_budget = Budzety.objects.get(pk=budget_id)
                current_users = selected_budget.users.all()
                form = AddUserToBudgetForm(budgets_qs=user_budgets, initial={'budget': selected_budget})
            except Budzety.DoesNotExist:
                pass

    return render(request, 'budzetApp/add_user_to_budget.html', {
        'form': form,
        'current_users': current_users,
        'selected_budget': selected_budget,
        'invite_link': invite_link,
    })

# Strona pobierania kategorii budżetu
def get_budget_categories(request):
    budget_id = request.GET.get('budget_id')
    categories = []
    if budget_id:
        categories = Kategorie.objects.filter(budget_id=budget_id)
    data = [{'id': c.id, 'name': c.category_name} for c in categories]
    return JsonResponse({'categories': data})

# Strona akceptacji zaproszenia do budżetu
def accept_invitation(request):
    token = request.GET.get('token')
    if not token:
        messages.error(request, "Brak tokena zaproszenia.")
        return redirect('budzetApp:index')

    user_id = request.session.get('user_id')
    if not user_id:

        next_url = f"{request.path}?token={token}"
        login_url = f"{reverse_lazy('budzetApp:login')}?{urlencode({'next': next_url})}"

        messages.info(request, "Zaloguj się, aby dołączyć do budżetu.")
        return redirect(login_url)

    invitation = get_object_or_404(BudgetInvitation, token=token, accepted=False)
    user = Uzytkownicy.objects.get(pk=user_id)
    budget = invitation.budget

    if user in budget.users.all():
        messages.info(request, "Jesteś już członkiem tego budżetu.")
    else:
        budget.users.add(user)
        invitation.accepted = True
        invitation.save()
        messages.success(request, f"Dołączyłeś do budżetu {budget.name}.")

    return redirect('budzetApp:index')

# Strona do opuszczania budzetow
def leave_budget(request, budget_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Musisz być zalogowany.")
        return redirect('budzetApp:login')

    user = Uzytkownicy.objects.get(pk=user_id)
    budget = get_object_or_404(Budzety, pk=budget_id)

    if user in budget.users.all():
        budget.users.remove(user)
        if budget.users.count() == 0:
            budget.delete()
        messages.success(request, f"Opuszczono budżet {budget.name}.")
    else:
        messages.info(request, "Nie jesteś członkiem tego budżetu.")

    return redirect('budzetApp:budget_list')

#----------------------------------------------------------------------

# Zarządzanie transakcjami

# Strona dodawania transakcji
def add_transaction(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You need to be logged, to add transaction.")
        return redirect('budzetApp:login')

    user = Uzytkownicy.objects.get(pk=user_id)
    # Budżety utworzone przez użytkownika lub do których ma dostęp
    budgets_qs = Budzety.objects.filter(users=user).distinct()

    if request.method == 'POST':
        form = TransakcjeForm(request.POST, budgets_qs=budgets_qs)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = user
            amount = transaction.amount
            is_expense = 'is_expense' in request.POST  # True jeśli zaznaczony

            if is_expense and amount > 0:
                transaction.amount = -amount

            transaction.save()
            return redirect('budzetApp:budget_list')
    else:
        form = TransakcjeForm(budgets_qs=budgets_qs)
    return render(request, 'budzetApp/addtransaction.html', {'form': form})

# Strona listy transakcji
'''def transaction_list(request):
    user_id = request.session['user_id']
    transactions = []
    if user_id:
        user = Uzytkownicy.objects.get(pk=user_id)
        transactions = Transakcje.objects.filter(user=user).order_by('-transaction_date')
    context = {
        'transactions': transactions
    }
    return render(request, 'budzetApp/transaction.html', context)'''

# Strona szczegółów transakcji
def transaction_detail(request, transaction_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Musisz być zalogowany, aby zobaczyć szczegóły transakcji.")
        return redirect('budzetApp:login')

    transaction = get_object_or_404(Transakcje, pk=transaction_id)
    # Opcjonalnie: sprawdź, czy użytkownik ma dostęp do tej transakcji
    if transaction.budget not in Budzety.objects.filter(users__id=user_id):
        messages.error(request, "Nie masz dostępu do tej transakcji.")
        return redirect('budzetApp:index')

    return render(request, 'budzetApp/transaction_detail.html', {'transaction': transaction})

    
#----------------------------------------------------------------------

# Zarządzanie kategoriami

# Strona tworzenia kategorii
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


# Strona pobierania użytkowników budżetu
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

#----------------------------------------------------------------------

