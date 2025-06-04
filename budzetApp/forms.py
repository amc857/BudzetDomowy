from typing import Any
from django import forms
from .models import Budget, Kategorie, Transaction, User
from django.core.exceptions import ValidationError

from .models import Budzety, Transakcje, Uzytkownicy


class TransakcjeForm(forms.ModelForm):
    class Meta:
        model = Transakcje
        fields = ['budget', 'category', 'amount', 'description']

    def __init__(self, *args, **kwargs):
        budgets_qs = kwargs.pop('budgets_qs', None)
        super().__init__(*args, **kwargs)
        if budgets_qs is not None:
            self.fields['budget'].queryset = budgets_qs


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Hasło")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Potwierdź hasło")

    class Meta:
        #model = User
        model = Uzytkownicy
        fields = ['username', 'password']

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


class KategorieCreateForm(forms.ModelForm):
    class Meta:
        model = Kategorie
        fields = ['category_name', 'budget']
        labels = {
            'category_name': 'Nazwa kategorii',
            'budget': 'Budżet',
        }

    def __init__(self, *args, **kwargs):
        budgets_qs = kwargs.pop('budgets_qs', None)
        super().__init__(*args, **kwargs)
        if budgets_qs is not None:
            self.fields['budget'].queryset = budgets_qs
    

class AddUserToBudgetForm(forms.Form):
    user = forms.ModelChoiceField(queryset=Uzytkownicy.objects.none(), label="Użytkownik")
    budget = forms.ModelChoiceField(queryset=Budzety.objects.all(), label="Budżet")

    def __init__(self, *args, **kwargs):
        budgets_qs = kwargs.pop('budgets_qs', None)
        selected_budget = kwargs.pop('selected_budget', None)
        super().__init__(*args, **kwargs)
        if budgets_qs is not None:
            self.fields['budget'].queryset = budgets_qs
        if selected_budget:
            self.fields['user'].queryset = Uzytkownicy.objects.exclude(budzety=selected_budget)
        else:
            self.fields['user'].queryset = Uzytkownicy.objects.all()