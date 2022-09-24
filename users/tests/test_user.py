from django.urls import reverse
from users import forms


def test_user_login(user, client):
    url = reverse('users:login')
    data = {'username': 'John', 'password': 'test1234'}

    response = client.post(url, data=data)

    assert response.status_code == 302


def test_user_can_create_account(client, db):
    url = reverse('users:register')
    data = {'username': 'Test', 'password': 'test1234', 'email': 'test@gmail.com', 'password_confirmation': 'test1234'}

    response = client.post(url, data=data)

    assert response.status_code == 302


def test_register_with_incorect_data(db):
    data = {'username': 'Test', 'password': 'test1234', 'email': 'gmail.com', 'password_confirmation': 'test123'}
    form = forms.RegistrationForm(data=data)

    assert len(form.errors) != 0


def test_login_with_incorect_data(db):
    data = {'username': 'badday', 'password': 'test1234'}
    form = forms.LoginForm(data=data)

    assert len(form.errors) != 0
