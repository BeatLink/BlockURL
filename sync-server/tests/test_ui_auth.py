"""The login flow, with the app running as it does when an API key is configured."""

import pytest
from nicegui.testing import User

from tests.conftest import TEST_API_KEY

pytestmark = pytest.mark.blockurl_api_key(TEST_API_KEY)


async def test_visiting_the_dashboard_lands_on_the_login_page(user: User):
    await user.open('/')
    await user.should_see('API Key')
    await user.should_not_see('Blocked Page Settings')


async def test_the_wrong_key_is_rejected(user: User):
    await user.open('/')
    user.find(marker='api-key').type('wrong')
    user.find('Sign in').click()
    await user.should_see('Invalid API key')
    await user.should_not_see('Blocked Page Settings')


async def test_the_right_key_opens_the_dashboard(user: User):
    await user.open('/')
    user.find(marker='api-key').type(TEST_API_KEY)
    user.find('Sign in').click()
    await user.should_see('Blocked Page Settings')


async def test_the_dashboard_stays_open_on_a_later_visit(user: User):
    await user.open('/')
    user.find(marker='api-key').type(TEST_API_KEY)
    user.find('Sign in').click()
    await user.should_see('Blocked Page Settings')

    await user.open('/')
    await user.should_see('Blocked Page Settings')


async def test_signing_out_sends_you_back_to_the_login_page(user: User):
    await user.open('/')
    user.find(marker='api-key').type(TEST_API_KEY)
    user.find('Sign in').click()
    await user.should_see('Blocked Page Settings')

    await user.open('/logout')
    await user.should_see('API Key')
