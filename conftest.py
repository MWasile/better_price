import pytest
from example_channels import consumers


@pytest.fixture(scope='function')
def user(db, django_user_model):
    return django_user_model.objects.create_user(email='a@a.pl', username='John', password='test1234')


@pytest.fixture(scope='function')
def logged_user(user, client):
    client.force_login(user)
    return client


@pytest.fixture
def cheated_ctx():
    """Overiding exit class."""

    class cheated(consumers.EbookHelper):
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return

    return cheated
