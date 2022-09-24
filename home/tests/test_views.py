from django.urls import reverse


def test_view_home(client):
    url = reverse('home:home')
    response = client.get(url)

    assert response.status_code == 200