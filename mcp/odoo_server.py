#!/usr/bin/env python3
"""
Odoo Accounting MCP Server
Handles accounting operations through JSON-RPC over stdio.
Connects to Odoo via XML-RPC. Credentials loaded from environment variables.
"""
import sys
import json
import os
import time
from datetime import datetime


class OdooMCPServer:
    def __init__(self):
        self.odoo_url = os.getenv('ODOO_URL', '')
        self.odoo_db = os.getenv('ODOO_DB', '')
        self.odoo_username = os.getenv('ODOO_USERNAME', '')
        self.odoo_api_key = os.getenv('ODOO_API_KEY', '')
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self._uid = None

    def _authenticate(self):
        """Authenticate with Odoo via XML-RPC"""
        if self._uid:
            return self._uid
        import xmlrpc.client
        try:
            common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            self._uid = common.authenticate(self.odoo_db, self.odoo_username, self.odoo_api_key, {})
            if not self._uid:
                raise Exception("Authentication returned no UID")
            return self._uid
        except Exception as e:
            raise ConnectionError(f"Odoo authentication failed: {e}")

    def _get_models(self):
        import xmlrpc.client
        return xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')

    def _make_response(self, request_id, result: dict) -> dict:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    def _make_error(self, request_id, code: int, message: str, data: dict | None = None) -> dict:
        error = {"code": code, "message": message}
        if data:
            error["data"] = data
        return {"jsonrpc": "2.0", "id": request_id, "error": error}

    def handle_request(self, request: dict) -> dict:
        method = request.get('method')
        request_id = request.get('id')
        params = request.get('params', {})

        handlers = {
            'create_expense': self.create_expense,
            'create_invoice': self.create_invoice,
            'get_financial_summary': self.get_financial_summary,
            'ping': lambda p: self._make_response(request_id, {"status": "ok", "server": "odoo"}),
        }

        handler = handlers.get(method)
        if not handler:
            return self._make_error(request_id, -32601, "Method not found")

        try:
            return handler(params)
        except ConnectionError as e:
            return self._make_error(request_id, -32001, str(e))
        except ValueError as e:
            return self._make_error(request_id, -32010, f"Validation error: {e}")
        except Exception as e:
            return self._make_error(request_id, -32000, f"Operation failed: {e}")

    def create_expense(self, params: dict) -> dict:
        request_id = params.get('id')
        description = params.get('description', '')
        amount = params.get('amount', 0)
        currency = params.get('currency', 'USD')
        category = params.get('category', 'general')
        date = params.get('date', datetime.now().strftime('%Y-%m-%d'))
        notes = params.get('notes', '')

        if not description or amount <= 0:
            raise ValueError("description and positive amount are required")

        if self.dry_run:
            return self._make_response(request_id, {
                "success": True,
                "expense_id": f"dry_run_{int(time.time())}",
                "dry_run": True,
                "message": f"Would create expense: {description} ({amount} {currency})",
            })

        uid = self._authenticate()
        models = self._get_models()
        expense_id = models.execute_kw(
            self.odoo_db, uid, self.odoo_api_key,
            'hr.expense', 'create', [{
                'name': description,
                'total_amount': amount,
                'date': date,
                'description': notes,
            }]
        )
        return self._make_response(request_id, {
            "success": True,
            "expense_id": str(expense_id),
            "amount": amount,
            "currency": currency,
        })

    def create_invoice(self, params: dict) -> dict:
        request_id = params.get('id')
        partner_name = params.get('partner_name', '')
        lines = params.get('lines', [])
        due_date = params.get('due_date', '')
        notes = params.get('notes', '')

        if not partner_name or not lines:
            raise ValueError("partner_name and lines are required")

        if self.dry_run:
            return self._make_response(request_id, {
                "success": True,
                "invoice_id": f"dry_run_{int(time.time())}",
                "dry_run": True,
                "message": f"Would create invoice for {partner_name}",
            })

        uid = self._authenticate()
        models = self._get_models()
        invoice_lines = []
        for line in lines:
            invoice_lines.append((0, 0, {
                'name': line.get('description', ''),
                'quantity': line.get('quantity', 1),
                'price_unit': line.get('price', 0),
            }))

        invoice_id = models.execute_kw(
            self.odoo_db, uid, self.odoo_api_key,
            'account.move', 'create', [{
                'partner_id': partner_name,
                'invoice_date_due': due_date,
                'narration': notes,
                'invoice_line_ids': invoice_lines,
                'move_type': 'out_invoice',
            }]
        )
        return self._make_response(request_id, {
            "success": True,
            "invoice_id": str(invoice_id),
        })

    def get_financial_summary(self, params: dict) -> dict:
        request_id = params.get('id')
        period = params.get('period', 'month')
        date = params.get('date', datetime.now().strftime('%Y-%m-%d'))

        if self.dry_run:
            return self._make_response(request_id, {
                "success": True,
                "dry_run": True,
                "summary": {"period": period, "date": date, "total_expenses": 0, "total_invoices": 0},
            })

        uid = self._authenticate()
        models = self._get_models()
        expenses = models.execute_kw(
            self.odoo_db, uid, self.odoo_api_key,
            'hr.expense', 'search_count', [[('date', '>=', date)]]
        )
        return self._make_response(request_id, {
            "success": True,
            "summary": {"period": period, "date": date, "expense_count": expenses},
        })


def main():
    server = OdooMCPServer()
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            print(json.dumps({
                "jsonrpc": "2.0", "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }), flush=True)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
