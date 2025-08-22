from django.urls import include, path

from . import views




app_name = "budzetApp"

urlpatterns = [
    
    path("", views.login, name='login'),
    path("login/", views.login, name='login'),
    path("index/", views.index, name="index"),
    path('addtransaction/', views.add_transaction, name='addtransaction'),
    path('register/', views.register, name='register'),
    path('create_budget/', views.create_budget, name='create_budget'),
    path('budget_list/', views.budget_list, name='budget_list'),
    path('transaction/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('transaction_detail_api/<int:pk>/', views.transaction_detail_api, name='transaction_detail_api'),
    path('create_category/', views.create_category, name='create_category'),
    path('add_user_to_budget/', views.add_user_to_budget, name='add_user_to_budget'),
    path('get_budget_users/', views.get_budget_users, name='get_budget_users'),
    path('logout/', views.logout_view, name='logout'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('accept_invitation/', views.accept_invitation, name='accept_invitation'),
    path('get_budget_categories/', views.get_budget_categories, name='get_budget_categories'),
    path('leave_budget/<int:budget_id>/', views.leave_budget, name='leave_budget'),
    path('delete_transaction/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('export/', views.export_data_view, name='export_data'),
    path('pdftemp/', views.pdf_temp, name='pdf_temp'),

]
