import pytest


@pytest.fixture(scope='function')
def user(db, django_user_model):
    return django_user_model.objects.create_user(email='a@a.pl', username='John', password='test1234')


@pytest.fixture(scope='function')
def logged_user(user, client):
    client.force_login(user)
    return client
