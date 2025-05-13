from django.urls import include, path

from . import views

from . import transaction_views



app_name = "budzetApp"

urlpatterns = [
    
    path("", views.login, name='login'),
    path("login/", views.login, name='login'),

    path("index/", transaction_views.index, name="index"),
    
    path('addtransaction/', transaction_views.add_transaction, name='addtransaction'),
    path('edit_transaction/<int:pk>/', transaction_views.edit_transaction, name='edit_transaction'),
    path('delete_transaction/<int:pk>/', transaction_views.delete_transaction, name='delete_transaction'),
    path('register/', views.register, name='register'),
    path('create_budget/', views.create_budget, name='create_budget'),
    path('budget_list/', views.budget_list, name='budget_list'),
]
