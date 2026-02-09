"""
Log Sanitizer
Removes PII and sensitive data from audit log entries before storage
"""
import re


# Patterns to sanitize
_EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
_PHONE_RE = re.compile(r'\+?\d[\d\s\-]{8,}\d')
_TOKEN_RE = re.compile(r'(Bearer\s+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE)

# Keys that should be masked entirely
_SENSITIVE_KEYS = {'password', 'token', 'secret', 'api_key', 'access_token', 'smtp_password'}


def sanitize_entry(entry: dict) -> dict:
    """Sanitize a log entry dict to remove PII and secrets"""
    return _sanitize_value(entry)


def _sanitize_value(value):
    if isinstance(value, dict):
        return {k: _sanitize_key_value(k, v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_value(v) for v in value]
    if isinstance(value, str):
        return _sanitize_string(value)
    return value


def _sanitize_key_value(key: str, value):
    if key.lower() in _SENSITIVE_KEYS:
        return "***REDACTED***"
    return _sanitize_value(value)


def _sanitize_string(text: str) -> str:
    text = _EMAIL_RE.sub('[EMAIL_REDACTED]', text)
    text = _PHONE_RE.sub('[PHONE_REDACTED]', text)
    text = _TOKEN_RE.sub(r'\1***REDACTED***', text)
    return text
