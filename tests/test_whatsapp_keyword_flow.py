"""
Tests for WhatsApp keyword-based auto-reply flow.
Covers: keyword detection, action file creation with message content,
approval file with draft reply, and end-to-end flow mock.
"""
import sys
import os
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
    """Create a minimal vault structure"""
    for d in ('Inbox', 'Needs_Action', 'Done', 'Pending_Approval', 'Approved',
              'Plans', 'Business', 'Briefings', 'Audit'):
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def watcher(vault):
    """WhatsAppWatcher with browser stubbed out (page=None until needed)"""
    from watchers.whatsapp_watcher import WhatsAppWatcher
    w = WhatsAppWatcher(str(vault), check_interval=5)
    # Prevent real browser launch
    w.page = None
    return w


@pytest.fixture
def watcher_custom_keywords(vault):
    from watchers.whatsapp_watcher import WhatsAppWatcher
    return WhatsAppWatcher(str(vault), trigger_keywords=['help', 'SOS'])


# ---------------------------------------------------------------------------
# 1. Keyword detection
# ---------------------------------------------------------------------------

class TestKeywordDetection:
    def test_contains_urgent(self, watcher):
        assert watcher._contains_trigger_keyword("This is urgent please respond")

    def test_contains_bhai_case_insensitive(self, watcher):
        assert watcher._contains_trigger_keyword("Bhai, need help")
        assert watcher._contains_trigger_keyword("BHAI please")
        assert watcher._contains_trigger_keyword("hello bhai")

    def test_no_keyword(self, watcher):
        assert not watcher._contains_trigger_keyword("Hello, how are you?")

    def test_empty_string(self, watcher):
        assert not watcher._contains_trigger_keyword("")

    def test_custom_keywords(self, watcher_custom_keywords):
        w = watcher_custom_keywords
        assert w._contains_trigger_keyword("I need help now")
        assert w._contains_trigger_keyword("SOS emergency")
        assert not w._contains_trigger_keyword("urgent matter")  # not in custom list


# ---------------------------------------------------------------------------
# 2. Action file creation with message content
# ---------------------------------------------------------------------------

class TestActionFileCreation:
    def test_action_file_contains_message_content(self, watcher):
        item = {
            'type': 'whatsapp_message',
            'contact': 'Ali',
            'message_text': 'Bhai, can you call me?',
            'timestamp': '2026-02-18T10:00:00',
            'status': 'unread',
        }
        path = watcher.create_action_file(item)
        content = path.read_text(encoding='utf-8')

        assert '## Message Content' in content
        assert 'Bhai, can you call me?' in content
        assert '## Draft Reply' in content
        assert 'Ali' in content

    def test_action_file_has_frontmatter(self, watcher):
        item = {
            'type': 'whatsapp_message',
            'contact': 'Sara',
            'message_text': 'urgent issue with order',
            'timestamp': '2026-02-18T11:00:00',
            'status': 'unread',
        }
        path = watcher.create_action_file(item)
        content = path.read_text(encoding='utf-8')

        assert 'action_type: whatsapp_message' in content
        assert 'contact: Sara' in content

    def test_draft_reply_mentions_urgent(self, watcher):
        item = {
            'type': 'whatsapp_message',
            'contact': 'Ahmed',
            'message_text': 'This is urgent!',
            'timestamp': '2026-02-18T12:00:00',
            'status': 'unread',
        }
        path = watcher.create_action_file(item)
        content = path.read_text(encoding='utf-8')

        assert 'urgent message' in content.lower()

    def test_draft_reply_generic_for_bhai(self, watcher):
        item = {
            'type': 'whatsapp_message',
            'contact': 'Imran',
            'message_text': 'Bhai, where are you?',
            'timestamp': '2026-02-18T12:30:00',
            'status': 'unread',
        }
        path = watcher.create_action_file(item)
        content = path.read_text(encoding='utf-8')

        assert "thank you for your message" in content.lower()

    def test_action_file_empty_message(self, watcher):
        """If message_text is missing, draft reply still generated"""
        item = {
            'type': 'whatsapp_message',
            'contact': 'Unknown',
            'timestamp': '2026-02-18T13:00:00',
            'status': 'unread',
        }
        path = watcher.create_action_file(item)
        content = path.read_text(encoding='utf-8')
        assert '## Draft Reply' in content


# ---------------------------------------------------------------------------
# 3. Approval file contains draft reply
# ---------------------------------------------------------------------------

class TestApprovalWithDraftReply:
    def test_approval_file_includes_draft_reply(self, vault):
        from utils.approval_formatter import ApprovalFormatter
        from models.approval_request import ApprovalRequest

        formatter = ApprovalFormatter(str(vault))
        request = ApprovalRequest(
            action_type='whatsapp_message',
            target='Ali',
            parameters={'source_file': 'whatsapp_Ali_123.md'},
            risk_level='medium',
            mcp_server='whatsapp_mcp',
            domain='personal',
        )
        draft = "Hi Ali, I received your urgent message and will get back to you shortly."
        path = formatter.create_approval_file(request, plan_summary="Reply to WhatsApp",
                                               draft_reply=draft)
        content = path.read_text(encoding='utf-8')

        assert '## Draft Reply' in content
        assert 'urgent message' in content
        assert 'Ali' in content

    def test_approval_file_without_draft_reply(self, vault):
        from utils.approval_formatter import ApprovalFormatter
        from models.approval_request import ApprovalRequest

        formatter = ApprovalFormatter(str(vault))
        request = ApprovalRequest(
            action_type='email_send',
            target='user@example.com',
            risk_level='low',
            mcp_server='email_mcp',
        )
        path = formatter.create_approval_file(request, plan_summary="Send email")
        content = path.read_text(encoding='utf-8')

        # No draft reply section for non-whatsapp
        assert '## Draft Reply' not in content


# ---------------------------------------------------------------------------
# 4. Gold processor — extract draft reply + routing
# ---------------------------------------------------------------------------

class TestGoldProcessorDraftReply:
    def test_extract_draft_reply(self):
        from processors.gold_processor import GoldProcessor

        content = """## Message Content
> Bhai help me

## Draft Reply
Hi Ali, thank you for your message. I'll review and respond soon.

## Action Required
Review the message.
"""
        # We only need the method, so create a minimal instance
        proc = GoldProcessor.__new__(GoldProcessor)
        reply = proc._extract_draft_reply(content)
        assert "thank you for your message" in reply.lower()

    def test_extract_draft_reply_empty(self):
        from processors.gold_processor import GoldProcessor

        content = "# Some file\n\nNo draft section here.\n"
        proc = GoldProcessor.__new__(GoldProcessor)
        reply = proc._extract_draft_reply(content)
        assert reply == ""

    def test_extract_message_content(self):
        from processors.gold_processor import GoldProcessor

        content = """## Message Content
> Bhai, urgent matter

## Draft Reply
Some reply
"""
        proc = GoldProcessor.__new__(GoldProcessor)
        msg = proc._extract_message_content(content)
        assert "urgent matter" in msg


# ---------------------------------------------------------------------------
# 5. End-to-end flow mock
# ---------------------------------------------------------------------------

class TestEndToEndFlow:
    def test_watcher_filters_non_keyword_messages(self, watcher):
        """Messages without keywords should NOT produce action files"""
        # Simulate page with one unread chat that has no keywords
        mock_badge = MagicMock()
        mock_title = MagicMock()
        mock_title.get_attribute.return_value = 'RandomPerson'

        mock_el = MagicMock()
        mock_el.query_selector.side_effect = lambda sel: {
            '[data-testid="icon-unread-count"]': mock_badge,
            'span[title]': mock_title,
        }.get(sel)

        mock_page = MagicMock()
        mock_page.query_selector_all.return_value = [mock_el]

        watcher.page = mock_page

        # _read_last_message returns text without keywords
        with patch.object(watcher, '_read_last_message', return_value='Hello there'):
            results = watcher.check_for_updates()
            assert len(results) == 0

    def test_watcher_includes_keyword_messages(self, watcher):
        """Messages WITH keywords should produce items"""
        mock_badge = MagicMock()
        mock_title = MagicMock()
        mock_title.get_attribute.return_value = 'Ali'

        mock_el = MagicMock()
        mock_el.query_selector.side_effect = lambda sel: {
            '[data-testid="icon-unread-count"]': mock_badge,
            'span[title]': mock_title,
        }.get(sel)

        mock_page = MagicMock()
        mock_page.query_selector_all.return_value = [mock_el]

        watcher.page = mock_page

        with patch.object(watcher, '_read_last_message', return_value='Bhai please help'):
            results = watcher.check_for_updates()
            assert len(results) == 1
            assert results[0]['message_text'] == 'Bhai please help'
            assert results[0]['contact'] == 'Ali'

    def test_full_flow_watcher_to_action_file(self, watcher):
        """Watcher detects keyword → creates action file with draft reply"""
        mock_badge = MagicMock()
        mock_title = MagicMock()
        mock_title.get_attribute.return_value = 'Usman'

        mock_el = MagicMock()
        mock_el.query_selector.side_effect = lambda sel: {
            '[data-testid="icon-unread-count"]': mock_badge,
            'span[title]': mock_title,
        }.get(sel)

        mock_page = MagicMock()
        mock_page.query_selector_all.return_value = [mock_el]

        watcher.page = mock_page

        with patch.object(watcher, '_read_last_message', return_value='This is urgent'):
            items = watcher.check_for_updates()
            assert len(items) == 1

            path = watcher.create_action_file(items[0])
            content = path.read_text(encoding='utf-8')

            assert 'Usman' in content
            assert 'This is urgent' in content
            assert '## Draft Reply' in content
            assert 'urgent message' in content.lower()


# ---------------------------------------------------------------------------
# 6. Settings — trigger keywords config
# ---------------------------------------------------------------------------

class TestSettingsKeywords:
    def test_default_keywords(self, monkeypatch):
        monkeypatch.delenv('WHATSAPP_TRIGGER_KEYWORDS', raising=False)
        from config.settings import load_config
        config = load_config()
        assert 'urgent' in config['WHATSAPP_TRIGGER_KEYWORDS']
        assert 'bhai' in config['WHATSAPP_TRIGGER_KEYWORDS']

    def test_custom_keywords_from_env(self, monkeypatch):
        monkeypatch.setenv('WHATSAPP_TRIGGER_KEYWORDS', 'help,SOS,asap')
        from config.settings import load_config
        config = load_config()
        assert 'help' in config['WHATSAPP_TRIGGER_KEYWORDS']
        assert 'SOS' in config['WHATSAPP_TRIGGER_KEYWORDS']
        assert 'asap' in config['WHATSAPP_TRIGGER_KEYWORDS']
