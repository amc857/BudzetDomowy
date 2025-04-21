from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Sum
from django.core.paginator import Paginator
from budzetApp.models import Transaction, Category
from budzetApp.forms import TransactionForm


def index(request):
    # Pobierz wszystkie transakcje posortowane według daty (od najnowszej)
    transaction_list = Transaction.objects.all().order_by('-transaction_date')
    
    # Paginacja - 10 transakcji na stronę
    paginator = Paginator(transaction_list, 10)
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)
    
    # Oblicz sumy dochodów i wydatków
    total_income = Transaction.objects.filter(
        amount__gt=0
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_expenses = Transaction.objects.filter(
        amount__lt=0
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Przygotuj kontekst dla szablonu
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