"""
Sensitive Action Detector
Detects actions that require HITL approval using keyword-based detection
"""
from config.settings import SENSITIVE_KEYWORDS


def requires_approval(content: str) -> bool:
    """Determine if content describes a sensitive action requiring human approval"""
    content_lower = content.lower()
    return any(keyword in content_lower for keyword in SENSITIVE_KEYWORDS)


def detect_action_type(content: str) -> str:
    """Detect the type of external action from content.
    Platform-explicit keywords checked first — if someone says
    'Post on LinkedIn about accounting', the action is linkedin_post.
    """
    content_lower = content.lower()

    # Platform-explicit checks first (most specific wins)
    # LinkedIn actions
    if 'linkedin' in content_lower:
        return 'linkedin_post'

    # Facebook actions
    if any(k in content_lower for k in ['facebook', 'fb post', 'post on facebook']):
        return 'facebook_post'

    # WhatsApp actions
    if any(k in content_lower for k in ['whatsapp', 'send message to']):
        return 'whatsapp_message'

    # Financial actions (Odoo)
    if any(k in content_lower for k in ['expense', 'invoice', 'accounting', 'bookkeeping', 'financial record']):
        return 'financial_action'
    if any(k in content_lower for k in ['payment', 'transaction', 'transfer', 'buy', 'purchase']):
        return 'financial_action'

    # Email actions
    if any(k in content_lower for k in ['email', 'send', 'smtp', 'mail']):
        return 'email_send'

    return 'general_action'


def assess_risk(content: str) -> str:
    """Assess risk level of an action"""
    content_lower = content.lower()

    high_risk = [
        'payment', 'transaction', 'transfer', 'purchase', 'buy', 'delete', 'remove',
        'expense', 'invoice', 'accounting', 'financial',
    ]
    if any(k in content_lower for k in high_risk):
        return 'high'

    medium_risk = ['email', 'send', 'post', 'publish', 'share', 'linkedin', 'facebook', 'whatsapp']
    if any(k in content_lower for k in medium_risk):
        return 'medium'

    return 'low'
