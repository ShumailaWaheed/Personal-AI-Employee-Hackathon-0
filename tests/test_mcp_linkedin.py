"""
LinkedIn MCP contract tests — US3: Social Media Operations
Tests create_post, get_post_metrics, ping, auth error, DRY_RUN.
"""
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.append(str(Path(__file__).parent.parent / 'mcp'))
sys.path.append(str(Path(__file__).parent.parent / 'src'))

import pytest


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv('LINKEDIN_ACCESS_TOKEN', 'test-token')
    monkeypatch.setenv('LINKEDIN_PERSONAL_ACCOUNT_ID', 'test-urn')
    monkeypatch.delenv('DRY_RUN', raising=False)


@pytest.fixture
def server():
    from linkedin_server import LinkedInMCPServer
    return LinkedInMCPServer()


class TestPing:
    def test_ping_returns_ok(self, server):
        resp = server.handle_request({"method": "ping", "id": "1", "params": {}})
        assert resp["result"]["status"] == "ok"


class TestCreatePost:
    def test_valid_post(self, server):
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.headers = {'x-restli-id': 'post_123'}
        mock_resp.json.return_value = {'id': 'post_123'}
        mock_resp.raise_for_status = MagicMock()

        with patch('linkedin_server.requests.post', return_value=mock_resp) as mock_post:
            resp = server.handle_request({
                "method": "create_post", "id": "1",
                "params": {"text": "Hello LinkedIn!"}
            })
            assert resp["result"]["success"] is True

    def test_missing_text(self, server):
        resp = server.handle_request({
            "method": "create_post", "id": "1",
            "params": {"text": ""}
        })
        assert "error" in resp

    def test_auth_error(self, server):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.raise_for_status.side_effect = Exception("401 Unauthorized")

        with patch('linkedin_server.requests.post', return_value=mock_resp):
            resp = server.handle_request({
                "method": "create_post", "id": "1",
                "params": {"text": "test"}
            })
            assert "error" in resp
            assert resp["error"]["code"] == -32001


class TestGetPostMetrics:
    def test_valid_metrics(self, server):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            'likesSummary': {'totalLikes': 15},
            'commentsSummary': {'totalFirstLevelComments': 3},
        }
        mock_resp.raise_for_status = MagicMock()

        with patch('linkedin_server.requests.get', return_value=mock_resp):
            resp = server.handle_request({
                "method": "get_post_metrics", "id": "1",
                "params": {"post_id": "post_123"}
            })
            assert resp["result"]["success"] is True
            assert resp["result"]["metrics"]["likes"] == 15


class TestDryRun:
    def test_post_dry_run(self, monkeypatch):
        monkeypatch.setenv('DRY_RUN', 'true')
        from linkedin_server import LinkedInMCPServer
        server = LinkedInMCPServer()

        resp = server.handle_request({
            "method": "create_post", "id": "1",
            "params": {"text": "Dry run post"}
        })
        assert resp["result"]["success"] is True
        assert resp["result"]["dry_run"] is True
