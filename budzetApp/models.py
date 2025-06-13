from django.db import models
from django.utils import timezone

# Create your models here.

# #-----------------------------------------------------------

class Uzytkownicy(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.username

class Budzety(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    budget_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    users = models.ManyToManyField(Uzytkownicy, through='UzytkownikBudzetPolaczenia', related_name='budzety')

    def __str__(self):
        return f"{self.name}({self.id})"

    def get_total_transactions(self, user):
        """
        Oblicza sumę transakcji przypisanych do tej kategorii i użytkownika.
        """
        transactions = Transakcje.objects.filter(
            category=self.category,
            user=user,
            transaction_date__month=self.date.month,
            transaction_date__year=self.date.year
        )
        return sum(transaction.amount for transaction in transactions)

class Kategorie(models.Model):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    budget = models.ForeignKey(Budzety, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.category_name

class Transakcje(models.Model):
    id = models.AutoField(primary_key=True)
    budget = models.ForeignKey(Budzety, on_delete=models.DO_NOTHING, null=True, blank=False)
    category = models.ForeignKey(Kategorie, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateField(auto_now_add=True)
    description = models.TextField()
    user = models.ForeignKey(Uzytkownicy, on_delete=models.DO_NOTHING)
    def __str__(self):
        return f"{self.amount} by {self.user.username} on {self.transaction_date}"

class UzytkownikBudzetPolaczenia(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Uzytkownicy, on_delete=models.CASCADE)
    budget = models.ForeignKey(Budzety, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)  # np. "owner", "viewer", "editor"
    class Meta:
        unique_together = ('user', 'budget')
    def __str__(self):
        return f"{self.user.username} - {self.budget.name} as {self.role}"

class BudgetInvitation(models.Model):
    invited_user = models.ForeignKey(Uzytkownicy, on_delete=models.CASCADE, related_name='invitations')
    budget = models.ForeignKey(Budzety, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    accepted = models.BooleanField(default=False)