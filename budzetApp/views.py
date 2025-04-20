from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Transaction, Category
from .forms import TransactionForm
from django.db.models import Sum

class TransactionListView(ListView):
    model = Transaction
    template_name = "budzetApp/index.html"
    context_object_name = "transactions"
    ordering = ['-transaction_date']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_income'] = Transaction.objects.filter(
            amount__gt=0
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        context['total_expenses'] = Transaction.objects.filter(
            amount__lt=0
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        return context

class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "budzetApp/addtransaction.html"
    success_url = reverse_lazy('budzetApp:index')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transaction'] = None
        context['categories'] = Category.objects.all()
        return context

class TransactionUpdateView(UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "budzetApp/addtransaction.html"
    success_url = reverse_lazy('budzetApp:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transaction'] = self.object
        context['categories'] = Category.objects.all()
        return context

class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = "budzetApp/confirm_delete.html"
    success_url = reverse_lazy('budzetApp:index')


def index(request):
    transactions = Transaction.objects.all().order_by('-transaction_date')[:10]
    total_income = Transaction.objects.filter(amount__gt=0).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = Transaction.objects.filter(amount__lt=0).aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'budzetApp/index.html', {
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
    })
