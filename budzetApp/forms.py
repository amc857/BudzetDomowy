from django import forms
from .models import Budget, Transaction, User
from django.core.exceptions import ValidationError

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
    transactions = forms.ModelMultipleChoiceField(
        queryset=Transaction.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Wybierz transakcje"
    )

    class Meta:
        model = Budget
        fields = ['budget_amount', 'date']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['transactions'].queryset = Transaction.objects.filter(user=user)