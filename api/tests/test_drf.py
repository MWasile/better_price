import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from scraper.models import EmailTaskInfo


def test_only_logged_user_can_create_email_task(client, user):
    url = reverse('api:email', kwargs={'title': 'ala', 'price': 2})

    response = client.post(url)
    assert response.status_code == 401

    us1 = user

    client.force_login(us1)
    response_logged = client.post(url)

    assert response_logged.status_code == 200


def test_created_model_exist(logged_user):
    url = reverse('api:email', kwargs={'title': 'ala', 'price': 2})

    logged_user.post(url)
    email_case_model = EmailTaskInfo.objects.filter(user_input_search='ala')

    assert len(email_case_model) == 1


def test_wrong_params(logged_user):
    url = reverse('api:email', kwargs={'title': 'ala', 'price': 2222222222, })

    bad_response = logged_user.post(url)

    assert bad_response.status_code == 406
