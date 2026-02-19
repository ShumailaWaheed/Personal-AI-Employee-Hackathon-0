"""
WhatsApp MCP contract tests — US3: Social Media Operations
Tests send_message, get_message_status, ping, session expired, DRY_RUN.
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
    monkeypatch.setenv('WHATSAPP_MODE', 'api')
    monkeypatch.setenv('WHATSAPP_API_TOKEN', 'test-token')
    monkeypatch.delenv('DRY_RUN', raising=False)


@pytest.fixture
def server():
    from whatsapp_server import WhatsAppMCPServer
    return WhatsAppMCPServer()


class TestPing:
    def test_ping_returns_ok(self, server):
        resp = server.handle_request({"method": "ping", "id": "1", "params": {}})
        assert resp["result"]["status"] == "ok"
        assert resp["result"]["mode"] == "api"


class TestSendMessage:
    def test_valid_message_api(self, server):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"messages": [{"id": "msg_123"}]}
        mock_resp.raise_for_status = MagicMock()

        with patch('whatsapp_server.requests.post', return_value=mock_resp):
            resp = server.handle_request({
                "method": "send_message", "id": "1",
                "params": {"to": "+1234567890", "message": "Hello!"}
            })
            assert resp["result"]["success"] is True
            assert resp["result"]["message_id"] == "msg_123"

    def test_missing_to(self, server):
        resp = server.handle_request({
            "method": "send_message", "id": "1",
            "params": {"to": "", "message": "Hello!"}
        })
        assert "error" in resp

    def test_session_expired_error(self, server):
        with patch('whatsapp_server.requests.post', side_effect=ConnectionError("session expired")):
            resp = server.handle_request({
                "method": "send_message", "id": "1",
                "params": {"to": "+1234567890", "message": "test"}
            })
            assert "error" in resp
            assert resp["error"]["code"] == -32031

    def test_playwright_mode(self, monkeypatch):
        monkeypatch.setenv('WHATSAPP_MODE', 'playwright')
        from whatsapp_server import WhatsAppMCPServer
        server = WhatsAppMCPServer()

        # Mock the browser automation chain
        mock_element = MagicMock()
        mock_page = MagicMock()
        mock_page.wait_for_selector.return_value = mock_element

        server._page = mock_page  # skip _ensure_browser

        resp = server.handle_request({
            "method": "send_message", "id": "1",
            "params": {"to": "+1234567890", "message": "PW test"}
        })
        assert resp["result"]["success"] is True
        assert resp["result"]["mode"] == "playwright"
        assert resp["result"]["to"] == "+1234567890"

    def test_playwright_contact_not_found(self, monkeypatch):
        monkeypatch.setenv('WHATSAPP_MODE', 'playwright')
        from whatsapp_server import WhatsAppMCPServer
        server = WhatsAppMCPServer()

        mock_search = MagicMock()
        mock_page = MagicMock()
        # First call returns search box, second raises (contact not found)
        mock_page.wait_for_selector.side_effect = [mock_search, Exception("Timeout")]

        server._page = mock_page

        resp = server.handle_request({
            "method": "send_message", "id": "1",
            "params": {"to": "Unknown Person", "message": "test"}
        })
        assert "error" in resp

    def test_playwright_session_expired(self, monkeypatch):
        monkeypatch.setenv('WHATSAPP_MODE', 'playwright')
        from whatsapp_server import WhatsAppMCPServer
        server = WhatsAppMCPServer()

        # _page is None so _ensure_browser runs — mock playwright to fail
        with patch('whatsapp_server.WhatsAppMCPServer._ensure_browser',
                   side_effect=ConnectionError("session expired")):
            resp = server.handle_request({
                "method": "send_message", "id": "1",
                "params": {"to": "+1234567890", "message": "test"}
            })
            assert "error" in resp
            assert resp["error"]["code"] == -32031


class TestGetMessageStatus:
    def test_valid_status(self, server):
        resp = server.handle_request({
            "method": "get_message_status", "id": "1",
            "params": {"message_id": "msg_123"}
        })
        assert resp["result"]["success"] is True

    def test_missing_id(self, server):
        resp = server.handle_request({
            "method": "get_message_status", "id": "1",
            "params": {"message_id": ""}
        })
        assert "error" in resp


class TestDryRun:
    def test_message_dry_run(self, monkeypatch):
        monkeypatch.setenv('DRY_RUN', 'true')
        from whatsapp_server import WhatsAppMCPServer
        server = WhatsAppMCPServer()

        resp = server.handle_request({
            "method": "send_message", "id": "1",
            "params": {"to": "+1234567890", "message": "Dry run"}
        })
        assert resp["result"]["success"] is True
        assert resp["result"]["dry_run"] is True
