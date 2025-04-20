from django.urls import path

from . import views

app_name = "budzetApp"



urlpatterns = [
    path("", views.login, name='login'),
    path("index/", views.index, name="index"),
    path("budget/", views.budget, name="budget"),
    path('budget/delete/<int:budget_id>/', views.delete_budget, name='delete_budget'),
    path('addtransaction/', views.add_transaction, name='addtransaction')
    
]
