"""Test core.http — timeout default, User-Agent, retry, rate limit (fix P1, P2, P3)."""

import responses

from seoinngabs.core import http
from seoinngabs.core.http import USER_AGENT, get_session, reset_session


def setup_function():
    reset_session()


def teardown_function():
    reset_session()


class TestSessionConfig:
    def test_user_agent_set(self):
        session = get_session()
        assert session.headers["User-Agent"] == USER_AGENT
        assert "SeOinNgabs" in session.headers["User-Agent"]

    def test_user_agent_not_python_requests_default(self):
        # fix P2: UA default python-requests tidak boleh dipakai
        session = get_session()
        assert not session.headers["User-Agent"].startswith("python-requests")


class TestTimeout:
    @responses.activate
    def test_default_timeout_passed(self):
        responses.add(responses.GET, "https://example.com/", body="ok")
        session = get_session()
        # requests hanya mengirim timeout bila diberikan; kita assert default konstanta
        assert http.DEFAULT_TIMEOUT == (10, 30)


class TestRetry:
    def test_retry_configured(self):
        session = get_session()
        adapter = session.get_adapter("https://example.com/")
        retry = adapter.max_retries
        assert retry.total == 2
        assert 429 in retry.status_forcelist
        assert retry.backoff_factor == 0.5

    def test_retry_limited_not_infinite(self):
        # fix P3: retry harus terbatas
        session = get_session()
        assert session.get_adapter("https://x.com/").max_retries.total <= 3
