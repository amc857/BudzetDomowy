from django.urls import include, path

from . import views




app_name = "budzetApp"

urlpatterns = [
    
    path("", views.login, name='login'),
    path("login/", views.login, name='login'),

    path("index/", views.index, name="index"),
    
    path('addtransaction/', views.add_transaction, name='addtransaction'),
    path('edit_transaction/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('delete_transaction/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('register/', views.register, name='register'),
    path('create_budget/', views.create_budget, name='create_budget'),
    path('budget_list/', views.budget_list, name='budget_list'),
    path('transakcje/', views.transaction_list, name='transaction_list'),

]
