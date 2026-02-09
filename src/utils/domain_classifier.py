"""
Domain Classifier
Determines if an action item belongs to personal, business, or cross-domain context
"""

BUSINESS_KEYWORDS = [
    'invoice', 'expense', 'revenue', 'client', 'vendor', 'tax',
    'accounting', 'bookkeeping', 'profit', 'budget', 'quarterly',
    'financial', 'payroll', 'contract', 'supplier', 'procurement',
]

PERSONAL_KEYWORDS = [
    'personal', 'home', 'family', 'calendar', 'reminder',
    'grocery', 'appointment', 'birthday', 'vacation', 'hobby',
    'health', 'fitness', 'recipe', 'private',
]

VALID_DOMAINS = ('personal', 'business', 'cross-domain')


def classify_domain(content: str, frontmatter: dict | None = None) -> str:
    """Classify domain from frontmatter field or keyword inference.

    Domain precedence:
    1. Frontmatter `domain:` field (if valid)
    2. Keyword inference from content
    3. Default: "personal"
    """
    # Check frontmatter first
    if frontmatter and 'domain' in frontmatter:
        fm_domain = str(frontmatter['domain']).lower().strip()
        if fm_domain in VALID_DOMAINS:
            return fm_domain

    # Keyword inference fallback
    content_lower = content.lower()

    has_business = any(kw in content_lower for kw in BUSINESS_KEYWORDS)
    has_personal = any(kw in content_lower for kw in PERSONAL_KEYWORDS)

    if has_business and has_personal:
        return 'cross-domain'
    if has_business:
        return 'business'
    if has_personal:
        return 'personal'

    return 'personal'
