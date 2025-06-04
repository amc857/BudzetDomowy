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
    path('transaction_list/', views.transaction_list, name='transaction_list'),
    path('create_category/', views.create_category, name='create_category'),
    path('add_user_to_budget/', views.add_user_to_budget, name='add_user_to_budget'),
    path('get_budget_users/', views.get_budget_users, name='get_budget_users'),
    path('logout/', views.logout_view, name='logout'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('accept_invitation/', views.accept_invitation, name='accept_invitation'),
    path('get_budget_categories/', views.get_budget_categories, name='get_budget_categories'),
]
