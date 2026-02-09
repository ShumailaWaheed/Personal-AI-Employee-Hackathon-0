"""
Twitter MCP contract tests — US3: Social Media Operations
Tests post_tweet, get_engagement_metrics, ping, rate limit error, DRY_RUN.
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
    monkeypatch.setenv('TWITTER_BEARER_TOKEN', 'test-bearer')
    monkeypatch.setenv('TWITTER_API_KEY', 'test-key')
    monkeypatch.setenv('TWITTER_API_SECRET', 'test-secret')
    monkeypatch.delenv('DRY_RUN', raising=False)


@pytest.fixture
def server():
    from twitter_server import TwitterMCPServer
    return TwitterMCPServer()


class TestPing:
    def test_ping_returns_ok(self, server):
        resp = server.handle_request({"method": "ping", "id": "1", "params": {}})
        assert resp["result"]["status"] == "ok"


class TestPostTweet:
    def test_valid_tweet(self, server):
        mock_response = MagicMock()
        mock_response.data = {'id': '12345'}

        with patch.object(server, '_get_client') as mock_client:
            mock_client.return_value.create_tweet.return_value = mock_response
            resp = server.handle_request({
                "method": "post_tweet", "id": "1",
                "params": {"text": "Hello from Gold tier!"}
            })
            assert resp["result"]["success"] is True
            assert resp["result"]["tweet_id"] == "12345"

    def test_missing_text(self, server):
        resp = server.handle_request({
            "method": "post_tweet", "id": "1",
            "params": {"text": ""}
        })
        assert "error" in resp

    def test_rate_limit_error(self, server):
        with patch.object(server, '_get_client') as mock_client:
            mock_client.return_value.create_tweet.side_effect = Exception("429 rate limit exceeded")
            resp = server.handle_request({
                "method": "post_tweet", "id": "1",
                "params": {"text": "test"}
            })
            assert "error" in resp
            assert resp["error"]["code"] == -32020


class TestGetEngagementMetrics:
    def test_valid_metrics(self, server):
        mock_tweet = MagicMock()
        mock_tweet.data.public_metrics = {
            "like_count": 10, "retweet_count": 5,
            "reply_count": 2, "impression_count": 1000,
        }

        with patch.object(server, '_get_client') as mock_client:
            mock_client.return_value.get_tweet.return_value = mock_tweet
            resp = server.handle_request({
                "method": "get_engagement_metrics", "id": "1",
                "params": {"tweet_id": "12345"}
            })
            assert resp["result"]["success"] is True
            assert resp["result"]["metrics"]["likes"] == 10


class TestDryRun:
    def test_tweet_dry_run(self, monkeypatch):
        monkeypatch.setenv('DRY_RUN', 'true')
        from twitter_server import TwitterMCPServer
        server = TwitterMCPServer()

        resp = server.handle_request({
            "method": "post_tweet", "id": "1",
            "params": {"text": "Dry run tweet"}
        })
        assert resp["result"]["success"] is True
        assert resp["result"]["dry_run"] is True

    def test_metrics_dry_run(self, monkeypatch):
        monkeypatch.setenv('DRY_RUN', 'true')
        from twitter_server import TwitterMCPServer
        server = TwitterMCPServer()

        resp = server.handle_request({
            "method": "get_engagement_metrics", "id": "1",
            "params": {"tweet_id": "123"}
        })
        assert resp["result"]["success"] is True
        assert resp["result"]["dry_run"] is True
