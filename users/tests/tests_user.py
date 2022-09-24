from django.urls import reverse


def test_user_login(user, client):
    url = reverse('users:login')
    data = {'username': 'John', 'password': 'test1234'}

    response = client.post(url, data=data)

    assert response.status_code == 302


def test_user_can_create_account(client, db):
    url = reverse('users:register')
    data = {'username': 'Test', 'password': 'test1234', 'email': 'test@gmail.com'}

    response = client.post(url, data=data)

    assert response.status_code == 302
