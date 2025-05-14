from django import forms
from .models import Budget, Transaction, User, UserBudget
from django.core.exceptions import ValidationError
from datetime import date

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_date', 'description', 'category']
        widgets = {
            'transaction_date8': forms.DateInput(attrs={'type': 'date'}),
        }


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
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Dodaj członków do budżetu"
    )

    class Meta:
        model = Budget
        fields = ['name', 'budget_amount', 'date']

    def save(self, user, commit=True):
        """
        Zapisuje budżet i przypisuje właściciela oraz członków.
        """
        budget = super().save(commit=False)
        if commit:
            budget.save()
            # Przypisz właściciela jako "owner"
            UserBudget.objects.create(user=user, budget=budget, role='owner')
            # Dodaj członków jako "viewer"
            for member in self.cleaned_data['members']:
                UserBudget.objects.create(user=member, budget=budget, role='viewer')
            Budget.objects.create(name=self.cleaned_data['name'], budget_amount=self.cleaned_data['budget_amount'], date=self.cleaned_data['date'])
        return budget