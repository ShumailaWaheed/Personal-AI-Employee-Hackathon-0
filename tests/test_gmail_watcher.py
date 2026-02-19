"""
Tests for GmailWatcher — constitution Section V compliance.
Covers: service init, inbox check, action file creation, deduplication, error handling.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent / 'src'))

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def vault(tmp_path):
    for d in ('Inbox', 'Needs_Action', 'Done'):
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def watcher(vault):
    from watchers.gmail_watcher import GmailWatcher
    w = GmailWatcher(str(vault), check_interval=60)
    w._service = None  # ensure no real API calls
    return w


def _make_message(msg_id, from_addr, subject, snippet="Preview text"):
    """Helper to build a Gmail API message response"""
    return {
        'id': msg_id,
        'snippet': snippet,
        'payload': {
            'headers': [
                {'name': 'From', 'value': from_addr},
                {'name': 'Subject', 'value': subject},
                {'name': 'Date', 'value': 'Tue, 18 Feb 2026 10:00:00 +0500'},
            ]
        }
    }


# ---------------------------------------------------------------------------
# 1. Service initialization
# ---------------------------------------------------------------------------

class TestServiceInit:
    def test_no_service_returns_empty(self, watcher):
        """Without service, check_for_updates returns []"""
        assert watcher._service is None
        # _ensure_service will fail (no google libs mocked), so returns []
        with patch.object(watcher, '_ensure_service'):
            results = watcher.check_for_updates()
            assert results == []

    def test_credentials_from_env(self, vault, monkeypatch):
        monkeypatch.setenv('GOOGLE_APPLICATION_CREDENTIALS', '/custom/creds.json')
        monkeypatch.setenv('GMAIL_TOKEN_FILE', '/custom/token.json')
        from watchers.gmail_watcher import GmailWatcher
        w = GmailWatcher(str(vault))
        assert w.credentials_file == '/custom/creds.json'
        assert w.token_file == '/custom/token.json'


# ---------------------------------------------------------------------------
# 2. Inbox check
# ---------------------------------------------------------------------------

class TestCheckForUpdates:
    def test_detects_unread_emails(self, watcher):
        mock_service = MagicMock()
        mock_service.users().messages().list().execute.return_value = {
            'messages': [{'id': 'msg_001'}, {'id': 'msg_002'}]
        }
        mock_service.users().messages().get().execute.side_effect = [
            _make_message('msg_001', 'ali@example.com', 'Meeting Tomorrow'),
            _make_message('msg_002', 'sara@example.com', 'Invoice Attached'),
        ]
        watcher._service = mock_service

        results = watcher.check_for_updates()
        assert len(results) == 2
        assert results[0]['type'] == 'email_received'
        assert results[0]['from'] == 'ali@example.com'
        assert results[0]['subject'] == 'Meeting Tomorrow'
        assert results[1]['subject'] == 'Invoice Attached'

    def test_deduplication(self, watcher):
        """Same message ID should not appear twice"""
        mock_service = MagicMock()
        mock_service.users().messages().list().execute.return_value = {
            'messages': [{'id': 'msg_dup'}]
        }
        mock_service.users().messages().get().execute.return_value = \
            _make_message('msg_dup', 'x@y.com', 'Test')
        watcher._service = mock_service

        first = watcher.check_for_updates()
        assert len(first) == 1

        # Second call — same ID, should be skipped
        mock_service.users().messages().list().execute.return_value = {
            'messages': [{'id': 'msg_dup'}]
        }
        second = watcher.check_for_updates()
        assert len(second) == 0

    def test_empty_inbox(self, watcher):
        mock_service = MagicMock()
        mock_service.users().messages().list().execute.return_value = {
            'messages': []
        }
        watcher._service = mock_service

        results = watcher.check_for_updates()
        assert results == []

    def test_no_messages_key(self, watcher):
        mock_service = MagicMock()
        mock_service.users().messages().list().execute.return_value = {}
        watcher._service = mock_service

        results = watcher.check_for_updates()
        assert results == []

    def test_api_error_returns_empty(self, watcher):
        mock_service = MagicMock()
        mock_service.users().messages().list().execute.side_effect = Exception("API Error")
        watcher._service = mock_service

        results = watcher.check_for_updates()
        assert results == []


# ---------------------------------------------------------------------------
# 3. Action file creation
# ---------------------------------------------------------------------------

class TestActionFileCreation:
    def test_creates_file_with_correct_content(self, watcher):
        item = {
            'type': 'email_received',
            'message_id': 'msg_100',
            'from': 'client@company.com',
            'subject': 'Urgent: Project Update',
            'date': 'Tue, 18 Feb 2026 10:00:00 +0500',
            'snippet': 'Hi, please review the attached document...',
            'timestamp': '2026-02-18T10:00:00',
        }
        path = watcher.create_action_file(item)

        assert path.exists()
        content = path.read_text(encoding='utf-8')

        assert '# Email Received: Urgent: Project Update' in content
        assert 'client@company.com' in content
        assert '## Preview' in content
        assert 'please review the attached document' in content
        assert 'action_type: email_received' in content

    def test_filename_sanitization(self, watcher):
        item = {
            'type': 'email_received',
            'message_id': 'msg_200',
            'from': 'x@y.com',
            'subject': 'Re: Hello! How are you? (urgent)',
            'date': '',
            'snippet': '',
            'timestamp': '2026-02-18T11:00:00',
        }
        path = watcher.create_action_file(item)
        # Filename should not contain special chars
        assert '!' not in path.name
        assert '?' not in path.name
        assert '(' not in path.name
        assert path.name.startswith('gmail_')

    def test_action_file_has_frontmatter(self, watcher):
        item = {
            'type': 'email_received',
            'message_id': 'msg_300',
            'from': 'boss@work.com',
            'subject': 'Q1 Report',
            'date': 'Mon, 17 Feb 2026',
            'snippet': 'Quarterly review attached',
            'timestamp': '2026-02-18T12:00:00',
        }
        path = watcher.create_action_file(item)
        content = path.read_text(encoding='utf-8')
        assert content.startswith('---')
        assert 'action_type: email_received' in content
        assert 'from: boss@work.com' in content

    def test_no_subject_fallback(self, watcher):
        item = {
            'type': 'email_received',
            'message_id': 'msg_400',
            'from': 'anon@mail.com',
            'subject': '(no subject)',
            'date': '',
            'snippet': '',
            'timestamp': '2026-02-18T13:00:00',
        }
        path = watcher.create_action_file(item)
        content = path.read_text(encoding='utf-8')
        assert '(no subject)' in content


# ---------------------------------------------------------------------------
# 4. Cleanup
# ---------------------------------------------------------------------------

class TestCleanup:
    def test_cleanup_clears_service(self, watcher):
        watcher._service = MagicMock()
        watcher.cleanup()
        assert watcher._service is None


# ---------------------------------------------------------------------------
# 5. Settings
# ---------------------------------------------------------------------------

class TestSettingsGmail:
    def test_gmail_config_in_settings(self):
        from config.settings import load_config
        config = load_config()
        assert 'GOOGLE_APPLICATION_CREDENTIALS' in config
        assert 'GMAIL_TOKEN_FILE' in config
