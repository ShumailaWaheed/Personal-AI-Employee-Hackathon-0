#!/usr/bin/env python3
"""
Facebook MCP Server
Handles Facebook posting operations through JSON-RPC over stdio.
Uses requests library for Facebook Graph API. Credentials from environment variables.
"""
import sys
import json
import os
import time
from datetime import datetime

import requests


class FacebookMCPServer:
    def __init__(self):
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN', '')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID', '')  # Optional: for page posting
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self.api_base = 'https://graph.facebook.com/v19.0'

    def _headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
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
            'ping': lambda p: self._make_response(request_id, {"status": "ok", "server": "facebook"}),
        }

        handler = handlers.get(method)
        if not handler:
            return self._make_error(request_id, -32601, "Method not found")

        try:
            return handler(params)
        except Exception as e:
            if 'unauthorized' in str(e).lower() or '401' in str(e) or '190' in str(e):
                return self._make_error(request_id, -32001, f"Authentication failed: {e}")
            return self._make_error(request_id, -32000, f"Operation failed: {e}")

    def create_post(self, params: dict) -> dict:
        request_id = params.get('id')
        message = params.get('message', '')
        link = params.get('link')  # Optional: share a link
        target = params.get('target', 'me')  # 'me' for profile, or page_id for page

        if not message and not link:
            return self._make_error(request_id, -32010, "message or link is required")

        if self.dry_run:
            return self._make_response(request_id, {
                "success": True,
                "post_id": f"dry_run_{int(time.time())}",
                "dry_run": True,
                "message": f"Would create Facebook post: {message[:50] if message else link}...",
            })

        # Use page ID if specified, otherwise use 'me' for personal profile
        endpoint = target if target != 'me' else 'me'
        if self.page_id and target == 'page':
            endpoint = self.page_id

        payload = {
            'access_token': self.access_token,
        }
        if message:
            payload['message'] = message
        if link:
            payload['link'] = link

        # Facebook Graph API - create post
        url = f'{self.api_base}/{endpoint}/feed'
        resp = requests.post(url, data=payload)

        if resp.status_code == 401 or resp.status_code == 190:
            raise ConnectionError("Facebook authentication failed - check access token")

        resp.raise_for_status()
        data = resp.json()

        post_id = data.get('id', '')
        return self._make_response(request_id, {
            "success": True,
            "post_id": str(post_id),
            "message": message or link,
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

        # Get post insights
        url = f'{self.api_base}/{post_id}'
        params_data = {
            'access_token': self.access_token,
            'fields': 'likes.summary(true),comments.summary(true),shares',
        }
        resp = requests.get(url, params=params_data)
        resp.raise_for_status()
        data = resp.json()

        return self._make_response(request_id, {
            "success": True,
            "post_id": post_id,
            "metrics": {
                "likes": data.get('likes', {}).get('summary', {}).get('total_count', 0),
                "comments": data.get('comments', {}).get('summary', {}).get('total_count', 0),
                "shares": data.get('shares', {}).get('count', 0),
            },
        })


def main():
    server = FacebookMCPServer()
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
