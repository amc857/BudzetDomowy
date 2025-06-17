from .models import Uzytkownicy

def session_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return {'session_user': Uzytkownicy.objects.get(id=user_id)}
        except Uzytkownicy.DoesNotExist:
            if 'user_id' in request.session:
                del request.session['user_id']
                request.session.modified = True 
            return {'session_user': None}
    return {'session_user': None}