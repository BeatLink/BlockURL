from blockurl.database import URL


def test_set_and_check_urls(database):
    database.set_urls(["https://example.com/a", "https://example.com/b"])
    result = database.get_urls_exist(["https://example.com/a", "https://example.com/c"])
    assert result == {
        "https://example.com/a": True,
        "https://example.com/c": False,
    }


def test_set_urls_extracts_domain(database):
    database.set_urls(["https://www.example.com/page"])
    rows = database.get_urls_sorted()
    assert len(rows) == 1
    url, domain, created_at = rows[0]
    assert url == "https://www.example.com/page"
    assert domain == "www.example.com"
    assert created_at is not None


def test_set_urls_is_idempotent(database):
    database.set_urls(["https://example.com/a"])
    database.set_urls(["https://example.com/a"])
    assert database.get_all_urls() == ["https://example.com/a"]


def test_set_urls_empty_list_noop(database):
    assert database.set_urls([]) == {"received": 0, "added": 0, "merged": 0}
    assert database.get_all_urls() == []


def test_set_urls_reports_added_and_merged(database):
    assert database.set_urls(["https://a.com/1", "https://a.com/2"]) == {
        "received": 2, "added": 2, "merged": 0,
    }
    assert database.set_urls(["https://a.com/2", "https://b.com/1"]) == {
        "received": 2, "added": 1, "merged": 1,
    }


def test_set_urls_counts_repeats_within_the_list_as_merged(database):
    assert database.set_urls(["https://a.com/1", "https://a.com/1"]) == {
        "received": 2, "added": 1, "merged": 1,
    }
    assert database.get_all_urls() == ["https://a.com/1"]


def test_delete_urls(database):
    database.set_urls(["https://example.com/a", "https://example.com/b"])
    database.delete_urls(["https://example.com/a"])
    assert database.get_all_urls() == ["https://example.com/b"]


def test_delete_urls_empty_list_noop(database):
    database.set_urls(["https://example.com/a"])
    assert database.delete_urls([]) is True
    assert database.get_all_urls() == ["https://example.com/a"]


def test_get_urls_exist_empty_list(database):
    assert database.get_urls_exist([]) == {}


def test_get_urls_sorted_by_url_ascending(database):
    database.set_urls(["https://b.com/", "https://a.com/"])
    rows = database.get_urls_sorted(order_by="url", descending=False)
    urls = [r[0] for r in rows]
    assert urls == ["https://a.com/", "https://b.com/"]


def test_get_urls_sorted_invalid_column_raises(database):
    try:
        database.get_urls_sorted(order_by="not_a_column")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_get_urls_sorted_filters_by_domain(database):
    database.set_urls(["https://a.com/1", "https://a.com/2", "https://b.com/1"])
    rows = database.get_urls_sorted(domain="a.com")
    assert {r[0] for r in rows} == {"https://a.com/1", "https://a.com/2"}


def test_get_stats_counts_urls_and_domains(database):
    database.set_urls(["https://a.com/1", "https://a.com/2", "https://b.com/1"])
    assert database.get_stats() == {"total_urls": 3, "unique_domains": 2}


def test_get_stats_on_empty_database(database):
    assert database.get_stats() == {"total_urls": 0, "unique_domains": 0}


def test_get_domains_with_counts(database):
    database.set_urls(["https://a.com/1", "https://a.com/2", "https://b.com/1"])
    counts = dict(database.get_domains_with_counts())
    assert counts["a.com"] == 2
    assert counts["b.com"] == 1


def test_settings_default_initialization(database):
    assert database.get_setting("blocked_page_heading_text") == "Blocked"
    assert database.get_setting("blocked_page_button_text") == "Unblock"


def test_set_setting_overwrites(database):
    database.set_setting("blocked_page_heading_text", "Nope!")
    assert database.get_setting("blocked_page_heading_text") == "Nope!"


def test_get_setting_missing_returns_none(database):
    assert database.get_setting("does_not_exist") is None


def test_get_all_settings_returns_tuples(database):
    settings = dict(database.get_all_settings())
    assert "blocked_page_heading_text" in settings


def test_extract_domain_handles_bare_host():
    assert URL  # sanity import check
    from blockurl.database import DatabaseManager
    assert DatabaseManager._extract_domain("example.com/page") == "example.com"
    assert DatabaseManager._extract_domain("https://example.com/page") == "example.com"
    assert DatabaseManager._extract_domain("https://EXAMPLE.com") == "example.com"
