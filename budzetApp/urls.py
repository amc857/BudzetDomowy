from django.urls import path

from . import views

app_name = "budzetApp"

urlpatterns = [
    path("", views.index, name="index"),
]
