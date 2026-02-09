#!/usr/bin/env python3
"""
LinkedIn MCP Server
Handles LinkedIn posting operations through JSON-RPC over stdio.
Uses requests library for LinkedIn API. Credentials from environment variables.
"""
import sys
import json
import os
import time
from datetime import datetime

import requests


class LinkedInMCPServer:
    def __init__(self):
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN', '')
        self.account_id = os.getenv('LINKEDIN_PERSONAL_ACCOUNT_ID', '')
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self.api_base = 'https://api.linkedin.com/v2'

    def _headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0',
        }

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
            'create_post': self.create_post,
            'get_post_metrics': self.get_post_metrics,
            'ping': lambda p: self._make_response(request_id, {"status": "ok", "server": "linkedin"}),
        }

        handler = handlers.get(method)
        if not handler:
            return self._make_error(request_id, -32601, "Method not found")

        try:
            return handler(params)
        except Exception as e:
            if 'unauthorized' in str(e).lower() or '401' in str(e):
                return self._make_error(request_id, -32001, f"Authentication failed: {e}")
            return self._make_error(request_id, -32000, f"Operation failed: {e}")

    def create_post(self, params: dict) -> dict:
        request_id = params.get('id')
        text = params.get('text', '')
        visibility = params.get('visibility', 'PUBLIC')

        if not text:
            return self._make_error(request_id, -32010, "text is required")

        if self.dry_run:
            return self._make_response(request_id, {
                "success": True,
                "post_id": f"dry_run_{int(time.time())}",
                "dry_run": True,
                "message": f"Would create LinkedIn post: {text[:50]}...",
            })

        # LinkedIn ugcPosts API - urn:li:person: format works for personal accounts
        author_urn = self.account_id if self.account_id.startswith('urn:li:') else f"urn:li:person:{self.account_id}"

        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility},
        }

        resp = requests.post(f'{self.api_base}/ugcPosts', headers=self._headers(), json=payload)
        if resp.status_code == 401:
            raise ConnectionError("401 Unauthorized: LinkedIn authentication failed")
        resp.raise_for_status()

        post_id = resp.headers.get('x-restli-id', resp.json().get('id', ''))
        return self._make_response(request_id, {
            "success": True,
            "post_id": str(post_id),
            "text": text,
        })

    def get_post_metrics(self, params: dict) -> dict:
        request_id = params.get('id')
        post_id = params.get('post_id', '')

        if not post_id:
            return self._make_error(request_id, -32010, "post_id is required")

        if self.dry_run:
            return self._make_response(request_id, {
                "success": True,
                "dry_run": True,
                "metrics": {"likes": 0, "comments": 0, "shares": 0},
            })

        resp = requests.get(
            f'{self.api_base}/socialActions/{post_id}',
            headers=self._headers(),
        )
        resp.raise_for_status()
        data = resp.json()

        return self._make_response(request_id, {
            "success": True,
            "post_id": post_id,
            "metrics": {
                "likes": data.get('likesSummary', {}).get('totalLikes', 0),
                "comments": data.get('commentsSummary', {}).get('totalFirstLevelComments', 0),
            },
        })


def main():
    server = LinkedInMCPServer()
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
