from django.db import models

# Create your models here.

from django.db import models

class User(models.Model):
    id = models.CharField(primary_key=True, max_length=36)  # UUID jako string
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    id = models.CharField(primary_key=True, max_length=36)  # UUID jako string
    category_name = models.CharField(max_length=100)
    is_income = models.BooleanField(default=False)  # True dla "income", False dla "expense"
    def __str__(self):
        return self.category_name

class Budget(models.Model):
    id = models.CharField(primary_key=True, max_length=36)  # UUID jako string
    budget_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.budget_amount} for {self.category}"

    def calculate_total_transactions(self, user):
        """
        Oblicza sumę transakcji przypisanych do tej kategorii i użytkownika.
        """
        transactions = Transaction.objects.filter(
            category=self.category,
            user=user,
            transaction_date__month=self.date.month,
            transaction_date__year=self.date.year
        )
        return sum(transaction.amount for transaction in transactions)
    
class UserBudget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)  # np. "owner", "viewer", "editor"

    class Meta:
        unique_together = ('user', 'budget')

    def __str__(self):
        return f"{self.user} - {self.budget} as {self.role}"

class Transaction(models.Model):
    id = models.CharField(primary_key=True, max_length=36)  # UUID jako string
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateField()
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.amount} by {self.user}"


class BudgetTransaction(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    def __str__(self):
        return f"Transaction {self.transaction.id} in Budget {self.budget.id}"