import os
import requests

_client_id = os.environ["SCROOGLE_CLIENT_ID"]
_client_secret = os.environ["SCROOGLE_CLIENT_SECRET"]
_refresh_token = os.environ["SCROOGLE_REFRESH_TOKEN"]
_access_token = os.environ.get("SCROOGLE_ACCESS_TOKEN", "please-refresh-me")

# 1 session object to store latest auth headers for all http calls:
_session = requests.Session()
_session.headers.update(
    {"User-Agent": "Scroogle", "Authorization": f"Bearer {_access_token}"}
)


def _do_refresh_token():
    url = "https://www.googleapis.com/oauth2/v4/token"
    resp = requests.post(
        url,
        data={
            "grant_type": "refresh_token",
            "client_id": _client_id,
            "client_secret": _client_secret,
            "refresh_token": _refresh_token,
        },
        headers={"User-Agent": "Scroogle"},
    )

    assert resp.status_code == 200, (resp.status_code, resp.text)

    result = resp.json()
    assert result["scope"] == "https://www.googleapis.com/auth/drive.file"

    token = result["access_token"]
    _session.headers.update({"Authorization": f"Bearer {token}"})


def _auth_method(method_name):
    session_method = getattr(_session, method_name)

    def result_func(*args, **kwargs):
        resp = session_method(*args, **kwargs)
        if resp.status_code == 401:
            _do_refresh_token()
            resp = session_method(*args, **kwargs)
        return resp

    return result_func


auth_get = _auth_method("get")
auth_post = _auth_method("post")
auth_put = _auth_method("put")


def ping():
    resp = auth_get("https://www.googleapis.com/drive/v3/about?fields=user")
    assert resp.status_code == 200, resp.content
    return resp.json()
