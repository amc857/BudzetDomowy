from typing import Any
from django import forms
from .models import Budget, Transaction, User
from django.core.exceptions import ValidationError

from .models import Budzety, Transakcje, Uzytkownicy


class TransakcjeForm(forms.ModelForm):
    class Meta:
        model = Transakcje
        fields = ['budget', 'category', 'amount', 'description']



class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Hasło")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Potwierdź hasło")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Hasła nie są zgodne.")
        return cleaned_data


class BudgetForm(forms.ModelForm):
    #transactions = forms.ModelMultipleChoiceField(
    #    queryset=Transakcje.objects.filter(user_id=),
    #    widget=forms.CheckboxSelectMultiple,
    #    required=False,
    #    label="Wybierz transakcje"
    #)

    class Meta:
        model = Budzety
        fields = ["name", "budget_amount", "users" ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['transactions'].queryset = Transakcje.objects.filter(user=user)
    

