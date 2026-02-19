#!/usr/bin/env python3
"""
Health check HTTP server for GCP Uptime Checks.
Uses stdlib only (no Flask) to minimize RAM on e2-micro (~25MB).
Endpoints:
  GET /health  - Full health report (JSON)
  GET /ready   - Simple readiness check (200 OK)
"""
import json
import os
import subprocess
import shutil
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
HEALTH_PORT = int(os.getenv('HEALTH_PORT', '8080'))
START_TIME = time.time()


def get_pm2_status() -> dict:
    """Query PM2 for process status."""
    try:
        result = subprocess.run(
            ['pm2', 'jlist'],
            capture_output=True, text=True, timeout=5
        )
        processes = json.loads(result.stdout)
        return {
            p['name']: {
                'status': p['pm2_env']['status'],
                'restarts': p['pm2_env']['restart_time'],
                'uptime': p['pm2_env'].get('pm_uptime', 0),
            }
            for p in processes
        }
    except Exception as e:
        return {'error': str(e)}


def get_disk_usage() -> dict:
    """Check disk usage."""
    try:
        total, used, free = shutil.disk_usage('/')
        return {
            'total_gb': round(total / (1024**3), 2),
            'used_gb': round(used / (1024**3), 2),
            'free_gb': round(free / (1024**3), 2),
            'used_pct': round(used / total * 100, 1),
        }
    except Exception:
        return {}


def get_vault_stats() -> dict:
    """Quick vault directory counts."""
    try:
        return {
            'inbox': len(list((VAULT_PATH / 'Inbox').glob('*.md'))),
            'needs_action': len(list((VAULT_PATH / 'Needs_Action').glob('*.md'))),
            'done': len(list((VAULT_PATH / 'Done').glob('*.md'))),
            'pending_approval': len(list((VAULT_PATH / 'Pending_Approval').glob('*.md'))),
        }
    except Exception:
        return {}


def get_last_log_entry() -> str:
    """Find the most recent log entry timestamp."""
    try:
        logs_dir = VAULT_PATH / 'Logs'
        log_files = sorted(logs_dir.glob('*.json'))
        if not log_files:
            return 'no logs yet'
        latest = log_files[-1]
        data = json.loads(latest.read_text())
        if data:
            return data[-1].get('timestamp', 'unknown')
        return 'empty log'
    except Exception:
        return 'unavailable'


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self._handle_health()
        elif self.path == '/ready':
            self._handle_ready()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_health(self):
        pm2 = get_pm2_status()
        disk = get_disk_usage()
        vault = get_vault_stats()

        unhealthy_processes = [
            name for name, info in pm2.items()
            if isinstance(info, dict) and info.get('status') not in ('online', 'launching')
        ]

        status = 'healthy' if not unhealthy_processes else 'degraded'
        http_code = 200 if status == 'healthy' else 503

        payload = {
            'status': status,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'uptime_seconds': round(time.time() - START_TIME),
            'deployment_mode': os.getenv('DEPLOYMENT_MODE', 'local'),
            'processes': pm2,
            'disk': disk,
            'vault': vault,
            'last_processed': get_last_log_entry(),
            'unhealthy': unhealthy_processes,
        }

        body = json.dumps(payload, indent=2).encode()
        self.send_response(http_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_ready(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')

    def log_message(self, format, *args):
        pass  # Suppress per-request logs


if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', HEALTH_PORT), HealthHandler)
    print(f'Health check server listening on port {HEALTH_PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print('Health check server stopped')
