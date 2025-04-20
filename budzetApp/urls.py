from django.urls import path
from .views import (
    TransactionListView,
    TransactionCreateView,
    TransactionUpdateView,
    TransactionDeleteView
)

app_name = 'budzetApp'

urlpatterns = [
    path('', TransactionListView.as_view(), name='index'),
    path('index/', TransactionListView.as_view(), name='index'),
    path('transaction/add/', TransactionCreateView.as_view(), name='add_transaction'),
    path('transaction/edit/<int:pk>/', TransactionUpdateView.as_view(), name='edit_transaction'),
    path('transaction/delete/<int:pk>/', TransactionDeleteView.as_view(), name='delete_transaction'),
]
