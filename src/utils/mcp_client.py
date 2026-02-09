"""
MCP Client Connector
Communicates with MCP servers via JSON-RPC over stdio
"""
import json
import subprocess
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for communicating with MCP servers via JSON-RPC over stdio"""

    # Server script routing map
    SERVER_SCRIPTS = {
        'email': 'email_server.py',
        'email_mcp': 'email_server.py',
        'odoo': 'odoo_server.py',
        'odoo_mcp': 'odoo_server.py',
        'facebook': 'facebook_server.py',
        'facebook_mcp': 'facebook_server.py',
        'linkedin': 'linkedin_server.py',
        'linkedin_mcp': 'linkedin_server.py',
        'whatsapp': 'whatsapp_server.py',
        'whatsapp_mcp': 'whatsapp_server.py',
    }

    def __init__(self, server_script: str | None = None):
        self.server_script = server_script or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'mcp', 'email_server.py'
        )
        self._mcp_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'mcp',
        )

    def _get_server_script(self, server_name: str) -> str:
        """Get the full path to the MCP server script for a given server name"""
        script_name = self.SERVER_SCRIPTS.get(server_name)
        if not script_name:
            return self.server_script  # Default to email
        return os.path.join(self._mcp_dir, script_name)

    def _call_server(self, server_name: str, method: str, params: dict | None = None) -> dict:
        """Make a JSON-RPC call to a specific MCP server by name"""
        script = self._get_server_script(server_name)
        return self._call(method, params, server_script=script)

    def _call(self, method: str, params: dict | None = None, server_script: str | None = None) -> dict:
        """Make a JSON-RPC call to the MCP server"""
        import time
        request = {
            "jsonrpc": "2.0",
            "id": f"req_{int(time.time())}",
            "method": method,
            "params": params or {},
        }
        request_json = json.dumps(request) + "\n"
        script = server_script or self.server_script

        try:
            proc = subprocess.run(
                ['python', script],
                input=request_json,
                capture_output=True,
                text=True,
                timeout=30,
                env=os.environ.copy(),
            )
            if proc.stdout.strip():
                return json.loads(proc.stdout.strip().split('\n')[0])
            if proc.stderr.strip():
                logger.error(f"MCP server stderr: {proc.stderr}")
            return {"error": {"code": -32000, "message": "No response from MCP server"}}
        except subprocess.TimeoutExpired:
            logger.error("MCP server timed out")
            return {"error": {"code": -32004, "message": "Server timed out"}}
        except FileNotFoundError:
            logger.error(f"MCP server script not found: {self.server_script}")
            return {"error": {"code": -32004, "message": "Server not found"}}
        except Exception as e:
            logger.error(f"MCP client error: {e}")
            return {"error": {"code": -32000, "message": str(e)}}

    def send_email(self, params: dict) -> bool:
        """Send an email via the Email MCP server"""
        response = self._call('send_email', params)
        if 'error' in response:
            logger.error(f"Email send failed: {response['error']}")
            return False
        result = response.get('result', {})
        return result.get('success', False)

    def validate_recipients(self, recipients: list[str]) -> dict:
        """Validate email recipients via the MCP server"""
        response = self._call('validate_recipients', {"recipients": recipients})
        return response.get('result', {})

    def ping(self) -> bool:
        """Health check for MCP server"""
        response = self._call('ping')
        return 'result' in response and response['result'].get('status') == 'ok'

    def get_account_info(self) -> dict:
        """Get email account info from MCP server"""
        response = self._call('get_account_info')
        return response.get('result', {})

    def ping_server(self, server_name: str) -> bool:
        """Health check for a specific MCP server by name"""
        response = self._call_server(server_name, 'ping')
        return 'result' in response and response['result'].get('status') == 'ok'

    # Odoo MCP methods
    def create_expense(self, params: dict) -> dict:
        """Create an expense via Odoo MCP"""
        response = self._call_server('odoo', 'create_expense', params)
        if 'error' in response:
            logger.error(f"Odoo create_expense failed: {response['error']}")
        return response.get('result', response)

    def create_invoice(self, params: dict) -> dict:
        """Create an invoice via Odoo MCP"""
        response = self._call_server('odoo', 'create_invoice', params)
        if 'error' in response:
            logger.error(f"Odoo create_invoice failed: {response['error']}")
        return response.get('result', response)

    def get_financial_summary(self, params: dict) -> dict:
        """Get financial summary via Odoo MCP"""
        response = self._call_server('odoo', 'get_financial_summary', params)
        return response.get('result', response)

    # Facebook MCP methods
    def create_facebook_post(self, params: dict) -> dict:
        """Post to Facebook via Facebook MCP"""
        response = self._call_server('facebook', 'create_post', params)
        if 'error' in response:
            logger.error(f"Facebook create_post failed: {response['error']}")
        return response.get('result', response)

    def get_facebook_post_metrics(self, params: dict) -> dict:
        """Get Facebook post metrics via Facebook MCP"""
        response = self._call_server('facebook', 'get_post_metrics', params)
        return response.get('result', response)

    # LinkedIn MCP methods
    def create_linkedin_post(self, params: dict) -> dict:
        """Create a LinkedIn post via LinkedIn MCP"""
        response = self._call_server('linkedin', 'create_post', params)
        if 'error' in response:
            logger.error(f"LinkedIn create_post failed: {response['error']}")
        return response.get('result', response)

    def get_linkedin_metrics(self, params: dict) -> dict:
        """Get LinkedIn post metrics via LinkedIn MCP"""
        response = self._call_server('linkedin', 'get_post_metrics', params)
        return response.get('result', response)

    # WhatsApp MCP methods
    def send_whatsapp(self, params: dict) -> dict:
        """Send a WhatsApp message via WhatsApp MCP"""
        response = self._call_server('whatsapp', 'send_message', params)
        if 'error' in response:
            logger.error(f"WhatsApp send_message failed: {response['error']}")
        return response.get('result', response)
