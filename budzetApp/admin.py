from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(User)
admin.site.register(Category)
admin.site.register(UserBudget)
admin.site.register(Budget)
admin.site.register(Transaction)

#----------------------------------------

admin.site.register(Uzytkownicy)
admin.site.register(Kategorie)
admin.site.register(UzytkownikBudzetPolaczenia)
admin.site.register(Budzety)
admin.site.register(Transakcje)