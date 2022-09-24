import pytest
from channels.testing import HttpCommunicator
from channels.layers import get_channel_layer
from example_channels.consumers import SimpleConsumer


@pytest.mark.asyncio
async def test_logged_user_state_in_ctx(cheated_ctx, user):
    async with cheated_ctx('channel_layer', 'user input', user) as cheat:
        user_is_auth = cheat.user_auth

    assert str(user_is_auth) == 'True'


@pytest.mark.asyncio
async def test_anonymous_state_in_ctx(cheated_ctx):
    async with cheated_ctx('channel_layer', 'user input', None) as cheat:
        user_is_auth = cheat.user_auth

    assert str(user_is_auth) == 'False'


# @pytest.mark.asyncio
# async def test_aexit_send_correct_data_to_layers():
#     communicator = HttpCommunicator(SimpleConsumer.as_asgi(), "GET", "ws/test/")
#     response = await communicator.get_response()
#
#     assert response == 'dupa'