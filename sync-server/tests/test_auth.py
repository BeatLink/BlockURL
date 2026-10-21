import json

import pytest

from blockurl.auth import PUBLIC_PREFIXES, hash_key, is_allowed, load_client_hashes, match_client, safe_next_path

CLIENT_HASHES = {"laptop": hash_key("laptop-key"), "phone": hash_key("phone-key")}


def test_each_client_key_resolves_to_its_name():
    assert match_client("laptop-key", CLIENT_HASHES) == "laptop"
    assert match_client("phone-key", CLIENT_HASHES) == "phone"


def test_wrong_key_matches_no_client():
    assert match_client("wrong", CLIENT_HASHES) is None


def test_missing_key_matches_no_client():
    assert match_client(None, CLIENT_HASHES) is None
    assert match_client("", CLIENT_HASHES) is None


def test_a_stored_hash_is_not_accepted_as_a_key():
    assert match_client(CLIENT_HASHES["laptop"], CLIENT_HASHES) is None


def test_hash_matches_sha256sum_of_the_key():
    # printf %s laptop-key | sha256sum
    assert hash_key("laptop-key") == "9b7b36061a684541007d2c543574a1db801bc8f41f85ac5fdc0155fe72a9ec38"


def test_hashes_file_is_read(tmp_path):
    path = tmp_path / "hashes.json"
    path.write_text(json.dumps({"laptop": CLIENT_HASHES["laptop"].upper()}))
    assert load_client_hashes(path) == {"laptop": CLIENT_HASHES["laptop"]}


def test_hashes_file_rejects_a_value_that_is_not_a_digest(tmp_path):
    path = tmp_path / "hashes.json"
    path.write_text(json.dumps({"laptop": "laptop-key"}))
    with pytest.raises(ValueError):
        load_client_hashes(path)


def test_matched_client_is_allowed():
    assert is_allowed("/urls/all", "laptop", False)


def test_unmatched_request_is_not_allowed():
    assert not is_allowed("/urls/all", None, False)


def test_signed_in_session_is_allowed():
    assert is_allowed("/urls/all", None, True)


def test_login_page_is_public():
    assert is_allowed("/login", None, False)


def test_nicegui_assets_are_public():
    for prefix in PUBLIC_PREFIXES:
        assert is_allowed(f"{prefix}anything", None, False)


def test_upload_endpoint_is_not_public():
    # Uploads are per-page routes under /_nicegui, and they write to the database.
    assert not is_allowed("/_nicegui/client/1/upload/2", None, False)


def test_next_path_keeps_a_local_path():
    assert safe_next_path("/urls/all") == "/urls/all"


def test_next_path_rejects_another_host():
    assert safe_next_path("//evil.example.com") == "/"
    assert safe_next_path("https://evil.example.com") == "/"


def test_next_path_defaults_to_root():
    assert safe_next_path("") == "/"
    assert safe_next_path(None) == "/"
