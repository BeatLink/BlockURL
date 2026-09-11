from blockurl.auth import PUBLIC_PREFIXES, is_allowed, safe_next_path

API_KEY = "test-secret-key"


def test_matching_header_key_is_allowed():
    assert is_allowed("/urls/all", API_KEY, False, API_KEY)


def test_wrong_header_key_is_not_allowed():
    assert not is_allowed("/urls/all", "wrong", False, API_KEY)


def test_missing_header_key_is_not_allowed():
    assert not is_allowed("/urls/all", None, False, API_KEY)


def test_signed_in_session_is_allowed():
    assert is_allowed("/urls/all", None, True, API_KEY)


def test_login_page_is_public():
    assert is_allowed("/login", None, False, API_KEY)


def test_nicegui_assets_are_public():
    for prefix in PUBLIC_PREFIXES:
        assert is_allowed(f"{prefix}anything", None, False, API_KEY)


def test_upload_endpoint_is_not_public():
    # Uploads are per-page routes under /_nicegui, and they write to the database.
    assert not is_allowed("/_nicegui/client/1/upload/2", None, False, API_KEY)


def test_next_path_keeps_a_local_path():
    assert safe_next_path("/urls/all") == "/urls/all"


def test_next_path_rejects_another_host():
    assert safe_next_path("//evil.example.com") == "/"
    assert safe_next_path("https://evil.example.com") == "/"


def test_next_path_defaults_to_root():
    assert safe_next_path("") == "/"
    assert safe_next_path(None) == "/"
