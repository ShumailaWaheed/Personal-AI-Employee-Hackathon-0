"""
Odoo MCP contract tests — US2: Business Accounting Automation
Tests create_expense, create_invoice, get_financial_summary, ping, auth error, validation error, DRY_RUN.
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
    monkeypatch.setenv('ODOO_URL', 'https://test.odoo.com')
    monkeypatch.setenv('ODOO_DB', 'testdb')
    monkeypatch.setenv('ODOO_USERNAME', 'admin')
    monkeypatch.setenv('ODOO_API_KEY', 'test-key')
    monkeypatch.delenv('DRY_RUN', raising=False)


@pytest.fixture
def server():
    from odoo_server import OdooMCPServer
    return OdooMCPServer()


class TestPing:
    def test_ping_returns_ok(self, server):
        resp = server.handle_request({"method": "ping", "id": "1", "params": {}})
        assert resp["result"]["status"] == "ok"


class TestCreateExpense:
    def test_valid_expense(self, server):
        with patch('xmlrpc.client.ServerProxy') as mock_proxy:
            mock_common = MagicMock()
            mock_common.authenticate.return_value = 1
            mock_models = MagicMock()
            mock_models.execute_kw.return_value = 42
            mock_proxy.side_effect = [mock_common, mock_models]

            resp = server.handle_request({
                "method": "create_expense", "id": "1",
                "params": {"description": "Software license", "amount": 500, "currency": "USD"}
            })
            assert resp["result"]["success"] is True
            assert resp["result"]["expense_id"] == "42"

    def test_validation_error_missing_description(self, server):
        resp = server.handle_request({
            "method": "create_expense", "id": "1",
            "params": {"description": "", "amount": 500}
        })
        assert "error" in resp
        assert resp["error"]["code"] == -32010

    def test_auth_failure(self, server):
        with patch('xmlrpc.client.ServerProxy') as mock_proxy:
            mock_common = MagicMock()
            mock_common.authenticate.return_value = None
            mock_proxy.return_value = mock_common

            resp = server.handle_request({
                "method": "create_expense", "id": "1",
                "params": {"description": "Test", "amount": 100}
            })
            assert "error" in resp
            assert resp["error"]["code"] == -32001


class TestCreateInvoice:
    def test_valid_invoice(self, server):
        with patch('xmlrpc.client.ServerProxy') as mock_proxy:
            mock_common = MagicMock()
            mock_common.authenticate.return_value = 1
            mock_models = MagicMock()
            mock_models.execute_kw.return_value = 99
            mock_proxy.side_effect = [mock_common, mock_models]

            resp = server.handle_request({
                "method": "create_invoice", "id": "1",
                "params": {
                    "partner_name": "Acme Corp",
                    "lines": [{"description": "Service", "quantity": 1, "price": 1000}],
                    "due_date": "2026-03-01",
                }
            })
            assert resp["result"]["success"] is True


class TestGetFinancialSummary:
    def test_summary(self, server):
        with patch('xmlrpc.client.ServerProxy') as mock_proxy:
            mock_common = MagicMock()
            mock_common.authenticate.return_value = 1
            mock_models = MagicMock()
            mock_models.execute_kw.return_value = 5
            mock_proxy.side_effect = [mock_common, mock_models]

            resp = server.handle_request({
                "method": "get_financial_summary", "id": "1",
                "params": {"period": "month"}
            })
            assert resp["result"]["success"] is True


class TestDryRun:
    def test_expense_dry_run(self, monkeypatch):
        monkeypatch.setenv('DRY_RUN', 'true')
        from odoo_server import OdooMCPServer
        server = OdooMCPServer()

        resp = server.handle_request({
            "method": "create_expense", "id": "1",
            "params": {"description": "Test", "amount": 100}
        })
        assert resp["result"]["success"] is True
        assert resp["result"]["dry_run"] is True

    def test_invoice_dry_run(self, monkeypatch):
        monkeypatch.setenv('DRY_RUN', 'true')
        from odoo_server import OdooMCPServer
        server = OdooMCPServer()

        resp = server.handle_request({
            "method": "create_invoice", "id": "1",
            "params": {"partner_name": "Test", "lines": [{"description": "x", "price": 1}]}
        })
        assert resp["result"]["success"] is True
        assert resp["result"]["dry_run"] is True
