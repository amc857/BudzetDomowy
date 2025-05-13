from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from budzetApp.models import Budget, BudgetTransaction, Category, Transaction, UserBudget, User
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BudgetForm, UserRegistrationForm



# Create your views here.



def login(request):
    
    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')



        # Sprawdzenie, czy użytkownik istnieje w bazie danych
        user = User.objects.filter(username=username, email=email, password=password)
        if user.exists():

            

            request.session['username'] = username
            request.session['email'] = email
            request.session['password'] = password

        

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
            # Pobierz wybrane transakcje z formularza (np. za pomocą checkboxów)
            selected_transactions = request.POST.getlist('transactions')  # Lista ID transakcji
            for transaction_id in selected_transactions:
                transaction = Transaction.objects.get(id=transaction_id)
                BudgetTransaction.objects.create(budget=budget, transaction=transaction)
            return redirect('budzetApp:budget_list')
    else:
        form = BudgetForm()
        transactions = Transaction.objects.filter(user=request.user)  # Transakcje użytkownika
    return render(request, 'budzetApp/create_budget.html', {'form': form})

def budget_list(request):
    budgets = Budget.objects.all()
    budget_summaries = []

    for budget in budgets:
        transactions = BudgetTransaction.objects.filter(budget=budget).select_related('transaction')
        total_transactions = sum(bt.transaction.amount for bt in transactions)
        budget_summaries.append({
            'budget': budget,
            'transactions': transactions,
            'total_transactions': total_transactions,
            'remaining': budget.budget_amount - total_transactions
        })

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
