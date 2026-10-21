"""The login flow, with the app running as it does when client keys are configured."""

import logging

import pytest
from nicegui.testing import User

from tests.conftest import TEST_CLIENT_KEYS

pytestmark = pytest.mark.blockurl_client_keys(TEST_CLIENT_KEYS)


async def sign_in(user: User, key):
    await user.open('/')
    user.find(marker='api-key').type(key)
    user.find('Sign in').click()


async def test_visiting_the_dashboard_lands_on_the_login_page(user: User):
    await user.open('/')
    await user.should_see('API Key')
    await user.should_not_see('Blocked Page Settings')


async def test_the_wrong_key_is_rejected(user: User):
    await sign_in(user, 'wrong')
    await user.should_see('Invalid API key')
    await user.should_not_see('Blocked Page Settings')


async def test_the_first_client_key_opens_the_dashboard(user: User):
    await sign_in(user, TEST_CLIENT_KEYS['laptop'])
    await user.should_see('Blocked Page Settings')


async def test_the_second_client_key_opens_the_dashboard(user: User):
    await sign_in(user, TEST_CLIENT_KEYS['phone'])
    await user.should_see('Blocked Page Settings')


async def test_signing_in_logs_the_client_name(user: User, caplog):
    with caplog.at_level(logging.INFO, logger='blockurl.auth'):
        await sign_in(user, TEST_CLIENT_KEYS['phone'])
        await user.should_see('Blocked Page Settings')
    assert 'client phone signed in to the web UI' in caplog.text


async def test_the_dashboard_stays_open_on_a_later_visit(user: User):
    await sign_in(user, TEST_CLIENT_KEYS['laptop'])
    await user.should_see('Blocked Page Settings')

    await user.open('/')
    await user.should_see('Blocked Page Settings')


async def test_signing_out_sends_you_back_to_the_login_page(user: User):
    await sign_in(user, TEST_CLIENT_KEYS['laptop'])
    await user.should_see('Blocked Page Settings')

    await user.open('/logout')
    await user.should_see('API Key')
