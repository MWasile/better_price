from django.urls import reverse
from scraper import models
from pytest_django.asserts import assertQuerysetEqual


def test_redirect_unlogged_user(client):
    response = client.get(reverse('dashboard:home'))
    assert response.status_code == 302


def test_dashboard_user_history_querryset(user, client):
    client.force_login(user)

    add_to_history = models.FastTaskInfo(user_input_search='Tomasz', search_for=user)
    add_to_history.save()

    response = client.get(reverse('dashboard:home'))

    qs = models.FastTaskInfo.objects.filter(user_input_search='Tomasz')

    assertQuerysetEqual(qs, response.context_data['user_results'])


def test_detail_view_querryset(user, client):
    client.force_login(user)
    user_inputs = ['somebook1', 'somebook2', 'somebook3']

    for user_input in user_inputs:
        new_record = models.FastTaskInfo(user_input_search=user_input, search_for=user)
        new_record.save()

    response = client.get(reverse('dashboard:detail', kwargs={'pk': user.id}))

    qs = models.ScrapEbookResult.objects.filter(object_id=user.id)

    assertQuerysetEqual(qs, response.context_data['details'])