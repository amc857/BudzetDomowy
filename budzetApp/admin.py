from django.contrib import admin
from .models import *

# Register your models here.


admin.site.register(Uzytkownicy)
admin.site.register(Kategorie)
admin.site.register(UzytkownikBudzetPolaczenia)
#admin.site.register(Budzety)
admin.site.register(Transakcje)

@admin.register(Budzety)
class BudzetyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'budget_amount', 'date', 'users_list')