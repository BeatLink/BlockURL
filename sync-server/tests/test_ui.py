"""End-to-end tests of the dashboard, driving the real entry point."""

import pytest
from nicegui import ui
from nicegui.testing import User

from blockurl.pages import _as_utc_iso, _format_count


def table_urls(user: User):
    """The URLs the table is showing; its rows are data, not rendered text."""
    table = next(iter(user.find(kind=ui.table).elements))
    return [row['url'] for row in table.rows]


async def test_dashboard_shows_every_section(user: User):
    await user.open('/')
    await user.should_see('BlockURL')
    await user.should_see('Overview')
    await user.should_see('Blocked Page Settings')
    await user.should_see('Import & Export')
    await user.should_see('Blocked URLs')


async def test_dashboard_shows_the_default_settings(user: User):
    await user.open('/')
    await user.should_see('Blocked')
    await user.should_see('This Page has been blocked by BlockURL')
    await user.should_see('Unblock')


async def test_adding_a_url_reports_it(user: User):
    await user.open('/')
    user.find(marker='add-url').type('https://example.com/one')
    user.find(marker='add-url-button').click()
    await user.should_see('URL blocked')
    assert table_urls(user) == ['https://example.com/one']


async def test_adding_the_same_url_twice_is_reported_as_already_blocked(user: User):
    await user.open('/')
    user.find(marker='add-url').type('https://example.com/one')
    user.find(marker='add-url-button').click()
    await user.should_see('URL blocked')

    user.find(marker='add-url').type('https://example.com/one')
    user.find(marker='add-url-button').click()
    await user.should_see('Already blocked')
    assert table_urls(user) == ['https://example.com/one']


async def test_adding_nothing_asks_for_a_url(user: User):
    await user.open('/')
    user.find(marker='add-url-button').click()
    await user.should_see('Enter a URL first')


async def test_a_trailing_slash_is_dropped_before_blocking(user: User):
    await user.open('/')
    user.find(marker='add-url').type('https://example.com/one/')
    user.find(marker='add-url-button').click()
    await user.should_see('URL blocked')
    assert table_urls(user) == ['https://example.com/one']


async def test_saving_settings_reports_success(user: User):
    await user.open('/')
    user.find(marker='blocked_page_heading_text').clear().type('Nope')
    user.find(marker='save-settings').click()
    await user.should_see('Settings saved')


async def test_saved_settings_come_back_on_the_next_visit(user: User):
    await user.open('/')
    user.find(marker='blocked_page_heading_text').clear().type('Nope')
    user.find(marker='save-settings').click()
    await user.should_see('Settings saved')

    await user.open('/')
    await user.should_see('Nope')


# Helpers ----------------------------------------------------------------------------------------

def test_counts_are_grouped_by_thousands():
    assert _format_count(1234567) == '1,234,567'


def test_a_missing_count_reads_as_zero():
    assert _format_count(None) == '0'


@pytest.mark.parametrize('stored', [
    '2026-09-11 19:01:34.282882+00:00',
    '2026-09-11 19:01:34',
])
def test_timestamps_are_normalised_to_utc(stored):
    # A stamp the browser can parse always carries its zone, whether or not the row had one.
    assert _as_utc_iso(stored).startswith('2026-09-11T19:01:34')
    assert _as_utc_iso(stored).endswith('+00:00')


def test_an_unparseable_timestamp_is_left_alone():
    assert _as_utc_iso('not a date') == 'not a date'


async def test_unblocking_a_url_removes_it(user: User):
    await user.open('/')
    user.find(marker='add-url').type('https://example.com/one')
    user.find(marker='add-url-button').click()
    await user.should_see('URL blocked')

    # The row's delete button lives in a Vue slot, so the table's event stands in for a click on it.
    user.find(kind=ui.table).trigger('unblock', {'url': 'https://example.com/one'})
    await user.should_see('Unblock this URL?')
    user.find(marker='confirm-unblock').click()
    await user.should_see('URL unblocked')
    assert table_urls(user) == []
