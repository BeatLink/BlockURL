import json


def test_index_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"BlockURL" in response.data


def test_settings_get_and_set(client):
    response = client.post(
        "/settings/set",
        json={"key": "blocked_page_heading_text", "value": "Nope"},
    )
    assert response.status_code == 200

    response = client.post(
        "/settings/get",
        json={"key": "blocked_page_heading_text"},
    )
    assert response.get_json() == "Nope"


def test_settings_all(client):
    response = client.get("/settings/all")
    settings = dict(response.get_json())
    assert "blocked_page_button_text" in settings


def test_urls_block_and_check(client):
    response = client.post("/urls/block", json={"urls": ["https://example.com/x"]})
    assert response.status_code == 200

    response = client.post("/urls/check", json={"urls": ["https://example.com/x", "https://other.com/"]})
    assert response.get_json() == {
        "https://example.com/x": True,
        "https://other.com/": False,
    }


def test_urls_unblock(client):
    client.post("/urls/block", json={"urls": ["https://example.com/x"]})
    response = client.post("/urls/unblock", json={"urls": ["https://example.com/x"]})
    assert response.status_code == 200

    response = client.post("/urls/check", json={"urls": ["https://example.com/x"]})
    assert response.get_json() == {"https://example.com/x": False}


def test_urls_all(client):
    client.post("/urls/block", json={"urls": ["https://example.com/x", "https://example.com/y"]})
    response = client.get("/urls/all")
    assert set(response.get_json()) == {"https://example.com/x", "https://example.com/y"}


def test_urls_sorted_default(client):
    client.post("/urls/block", json={"urls": ["https://example.com/x"]})
    response = client.post("/urls/sorted", json={})
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["url"] == "https://example.com/x"
    assert data[0]["domain"] == "example.com"
    assert "created_at" in data[0]


def test_urls_sorted_invalid_order_by_returns_400(client):
    response = client.post("/urls/sorted", json={"order_by": "nope"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_urls_sorted_filters_by_domain(client):
    client.post("/urls/block", json={"urls": ["https://a.com/1", "https://b.com/1"]})
    response = client.post("/urls/sorted", json={"domain": "a.com"})
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["domain"] == "a.com"


def test_urls_domains(client):
    client.post("/urls/block", json={"urls": ["https://a.com/1", "https://a.com/2"]})
    response = client.get("/urls/domains")
    domains = dict(response.get_json())
    assert domains["a.com"] == 2


def test_urls_block_unescapes_html_entities(client):
    # html.unescape is applied to incoming URLs - make sure entities round-trip
    client.post("/urls/block", json={"urls": ["https://example.com/?a=1&amp;b=2"]})
    response = client.get("/urls/all")
    assert "https://example.com/?a=1&b=2" in response.get_json()


# Input validation ---------------------------------------------------------------------------------

def test_settings_get_wrong_content_type_returns_error(client):
    response = client.post("/settings/get", data="not json", content_type="text/plain")
    assert response.status_code in (400, 415)

def test_settings_get_missing_key_returns_400(client):
    response = client.post("/settings/get", json={})
    assert response.status_code == 400

def test_settings_set_missing_value_returns_400(client):
    response = client.post("/settings/set", json={"key": "k"})
    assert response.status_code == 400

def test_urls_check_missing_urls_returns_400(client):
    response = client.post("/urls/check", json={})
    assert response.status_code == 400

def test_urls_block_missing_urls_returns_400(client):
    response = client.post("/urls/block", json={})
    assert response.status_code == 400

def test_urls_unblock_missing_urls_returns_400(client):
    response = client.post("/urls/unblock", json={})
    assert response.status_code == 400

def test_urls_block_non_list_returns_400(client):
    response = client.post("/urls/block", json={"urls": "https://example.com"})
    assert response.status_code == 400

def test_urls_block_url_too_long_returns_400(client):
    long_url = "https://example.com/" + "a" * 2048
    response = client.post("/urls/block", json={"urls": [long_url]})
    assert response.status_code == 400

def test_urls_block_list_too_large_returns_400(client):
    urls = [f"https://example.com/{i}" for i in range(10_001)]
    response = client.post("/urls/block", json={"urls": urls})
    assert response.status_code == 400


# Authentication -----------------------------------------------------------------------------------

from tests.conftest import TEST_API_KEY

def test_auth_unauthenticated_redirects_to_login(auth_client):
    response = auth_client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_auth_api_key_header_allows_access(auth_client):
    response = auth_client.get("/urls/all", headers={"X-API-Key": TEST_API_KEY})
    assert response.status_code == 200

def test_auth_wrong_api_key_header_redirects(auth_client):
    response = auth_client.get("/urls/all", headers={"X-API-Key": "wrong"})
    assert response.status_code == 302

def test_auth_login_page_renders(auth_client):
    response = auth_client.get("/login")
    assert response.status_code == 200
    assert b"BlockURL" in response.data

def test_auth_login_correct_key_sets_session_and_redirects(auth_client):
    response = auth_client.post("/login", data={"api_key": TEST_API_KEY}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

def test_auth_login_wrong_key_shows_error(auth_client):
    response = auth_client.post("/login", data={"api_key": "wrong"})
    assert response.status_code == 200
    assert b"Invalid" in response.data

def test_auth_session_allows_access_after_login(auth_client):
    auth_client.post("/login", data={"api_key": TEST_API_KEY})
    response = auth_client.get("/urls/all")
    assert response.status_code == 200

def test_auth_logout_clears_session(auth_client):
    auth_client.post("/login", data={"api_key": TEST_API_KEY})
    auth_client.get("/logout")
    response = auth_client.get("/urls/all")
    assert response.status_code == 302

def test_no_auth_configured_allows_all(client):
    response = client.get("/urls/all")
    assert response.status_code == 200