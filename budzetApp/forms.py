from django import forms
from .models import Transaction, User
from django.core.exceptions import ValidationError

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_date', 'description', 'category']
        widgets = {
            'transaction_date': forms.DateInput(attrs={'type': 'date'}),
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