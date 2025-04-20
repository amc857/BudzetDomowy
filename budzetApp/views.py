from django.shortcuts import render
from django.http import HttpResponseRedirect
from budzetApp.models import Budget, Category, Group
from django.shortcuts import render, redirect
from django.contrib import messages



# Create your views here.

def index(request):
    return render(request,"budzetApp/index.html")


def login(request):
    return render(request, 'budzetApp/login.html')

def budget(request):    
    budgets = Budget.objects.all()
    categories = Category.objects.all()
    groups = Group.objects.all()

    context = {
        'budgets': budgets,
        'categories': categories,
        'groups': groups
    }

    if request.method == 'POST':
        # Pobierz dane z formularza
        budget_amount = request.POST.get('budget_amount')
        date = request.POST.get('date')
        category_id = request.POST.get('category')
        group_id = request.POST.get('group')
        
        try:
            # Przekształć dane do odpowiednich typów
            budget_amount = float(budget_amount)
            
            # Pobierz obiekty powiązane
            category = Category.objects.get(id=category_id)
            group = Group.objects.get(id=group_id)
            
            # Utwórz nowy budżet
            new_budget = Budget.objects.create(
                budget_amount=budget_amount,
                date=date,
                category=category,
                group=group
            )
            
            messages.success(request, "Budżet został pomyślnie utworzony!")
            return redirect('budzetApp:budget')
        
        except ValueError:
            messages.error(request, "Nieprawidłowa wartość kwoty budżetu.")
        except Category.DoesNotExist:
            messages.error(request, "Wybrana kategoria nie istnieje.")
        except Group.DoesNotExist:
            messages.error(request, "Wybrana grupa nie istnieje.")
        except Exception as e:
            messages.error(request, f"Wystąpił błąd: {str(e)}")
    
    return render(request, 'budzetApp/budget.html', context)

def delete_budget(request, budget_id):
    try:
        budget = Budget.objects.get(id=budget_id)
        budget.delete()
        messages.success(request, "Budżet został pomyślnie usunięty.")
    except Budget.DoesNotExist:

        messages.error(request, "Budżet nie istnieje.")
        pass
    
    return redirect('budzetApp:budget')



def add_transaction(request):
     return render(request,'budzetApp/addtransaction.html')