from django.urls import include, path

from . import views

from . import transaction_views



app_name = "budzetApp"

urlpatterns = [
    
    path("", views.login, name='login'),
    path("login/", views.login, name='login'),

    path("index/", transaction_views.index, name="index"),
    path("budget/", views.budget, name="budget"),
    path('budget/delete/<int:budget_id>/', views.delete_budget, name='delete_budget'),
    path('budget/details/<int:budget_id>/', views.budget_details, name='budget_details'),
    
    path('addtransaction/', transaction_views.add_transaction, name='addtransaction'),
    path('edit_transaction/<int:pk>/', transaction_views.edit_transaction, name='edit_transaction'),
    path('delete_transaction/<int:pk>/', transaction_views.delete_transaction, name='delete_transaction'),

    path('groups/', views.groups, name='groups'),

]
