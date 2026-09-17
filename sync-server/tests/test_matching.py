import pytest

from blockurl.matching import match_key


@pytest.mark.parametrize("url, expected", [
    ("https://example.com/page", "example.com/page"),
    ("http://example.com/page", "example.com/page"),
    ("https://www.example.com/page", "example.com/page"),
    ("https://EXAMPLE.com/page", "example.com/page"),
    ("https://example.com/page/", "example.com/page"),
    ("https://example.com/page#section", "example.com/page"),
    ("https://example.com:443/page", "example.com/page"),
    ("http://example.com:80/page", "example.com/page"),
    ("https://example.com:8443/page", "example.com:8443/page"),
    ("https://example.com/", "example.com"),
])
def test_spellings_of_one_page_share_a_key(url, expected):
    assert match_key(url) == expected


def test_query_parameters_are_ordered_and_stripped_of_tracking():
    assert match_key("https://example.com/p?b=2&a=1") == match_key("https://example.com/p?a=1&b=2")
    assert match_key("https://example.com/p?a=1&utm_source=reddit&fbclid=x") == "example.com/p?a=1"


def test_query_parameters_still_distinguish_pages():
    assert match_key("https://youtube.com/watch?v=one") != match_key("https://youtube.com/watch?v=two")


@pytest.mark.parametrize("url", [
    "https://www.redgifs.com/watch/AbleGoat",
    "https://redgifs.com/ifr/ablegoat",
    "https://v3.redgifs.com/i/AbleGoat",
    "https://media.redgifs.com/AbleGoat-mobile.mp4",
    "https://thumbs2.redgifs.com/AbleGoat-small.jpg",
])
def test_redgifs_embeds_and_media_fold_onto_the_watch_page(url):
    assert match_key(url) == "redgifs.com/watch/ablegoat"


def test_different_redgifs_pages_stay_apart():
    assert match_key("https://redgifs.com/ifr/one") != match_key("https://redgifs.com/ifr/two")


@pytest.mark.parametrize("url", ["about:srcdoc", "blob:https://example.com/id", "data:text/html,hi", ""])
def test_non_web_urls_pass_through_unchanged(url):
    assert match_key(url) == url
