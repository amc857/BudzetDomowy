"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import django
from django.test import TestCase

# TODO: Configure your database in settings.py and sync before running tests.

class UserRegistrationTest(TestCase):
    def test_register_user(self):
        response = self.client.post(reverse('budzetApp:register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)  # przekierowanie po sukcesie
        self.assertTrue(Uzytkownicy.objects.filter(username='testuser').exists())

class UserLoginTest(TestCase):
    def setUp(self):
        self.user = Uzytkownicy.objects.create(username='testuser', email='test@example.com', password='testpass123')

    def test_login_user(self):
        response = self.client.post(reverse('budzetApp:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)  # przekierowanie po sukcesie

class BudgetTest(TestCase):
    def setUp(self):
        self.user = Uzytkownicy.objects.create(username='testuser', email='test@example.com', password='testpass123')
        self.client.session['user_id'] = self.user.id
        self.client.session.save()

    def test_create_budget(self):
        response = self.client.post(reverse('budzetApp:create_budget'), {
            'name': 'Bud¿et testowy',
            'budget_amount': 1000,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Budzety.objects.filter(name='Bud¿et testowy').exists())

    def test_index_view(self):
        Budzety.objects.create(name='Bud¿et testowy', budget_amount=1000)
        response = self.client.get(reverse('budzetApp:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Strona g³ówna")