from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from budzetApp.models import Budget, Category, Group, User
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm



# Create your views here.



def login(request):
    
    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')



        # Sprawdzenie, czy użytkownik istnieje w bazie danych
        user = User.objects.filter(username=username, email=email, password=password)
        if user.exists():

            

            request.session['username'] = username
            request.session['email'] = email
            request.session['password'] = password

        

            return redirect('budzetApp:index')
        else:
            # Użytkownik nie istnieje
            messages.error(request, "Nie znaleziono użytkownika o podanych danych.")
            return redirect('budzetApp:login')
        
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

        budget_amount = request.POST.get('budget_amount')
        date = request.POST.get('date')
        category_id = request.POST.get('category')
        group_id = request.POST.get('group')
        
        try:

            budget_amount = float(budget_amount)
            
            category = Category.objects.get(id=category_id)
            group = Group.objects.get(id=group_id)

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



def budget_details(request, budget_id):

    budget = get_object_or_404(Budget, id=budget_id)

    context = {
        'budget': budget
    }

    return render(request, 'budzetApp/budget_details.html', context)


def groups(request):
    groups = Group.objects.all()
    
    context = {
        'groups': groups
    }
    return render(request, 'budzetApp/groups.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
           
            user = form.save(commit=False)
            user.password = form.cleaned_data['password'] 
            user.save()
            messages.success(request, "Rejestracja zakończona sukcesem! Możesz się teraz zalogować.")
            return redirect('budzetApp:login') 
    else:
        form = UserRegistrationForm()
    return render(request, 'budzetApp/register.html', {'form': form})
