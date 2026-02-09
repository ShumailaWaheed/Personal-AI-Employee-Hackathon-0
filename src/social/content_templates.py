"""
Content Templates
Templates for LinkedIn post generation based on Company_Handbook.md
"""


TEMPLATES = {
    "company_update": {
        "structure": "Opening hook → Update details → Call to action",
        "tone": "Professional and informative",
        "template": (
            "{hook}\n\n"
            "{details}\n\n"
            "{cta}\n\n"
            "{hashtags}"
        ),
    },
    "industry_insight": {
        "structure": "Observation → Analysis → Question",
        "tone": "Thought leadership",
        "template": (
            "{observation}\n\n"
            "{analysis}\n\n"
            "{question}\n\n"
            "{hashtags}"
        ),
    },
    "milestone": {
        "structure": "Achievement → Context → Gratitude",
        "tone": "Celebratory and authentic",
        "template": (
            "{achievement}\n\n"
            "{context}\n\n"
            "{gratitude}\n\n"
            "{hashtags}"
        ),
    },
    "tip_share": {
        "structure": "Problem → Solution → Benefit",
        "tone": "Helpful and practical",
        "template": (
            "{problem}\n\n"
            "Here's what works:\n{solution}\n\n"
            "{benefit}\n\n"
            "{hashtags}"
        ),
    },
}


def get_template(template_type: str) -> dict:
    """Get a content template by type"""
    return TEMPLATES.get(template_type, TEMPLATES["company_update"])


def list_templates() -> list[str]:
    """List available template types"""
    return list(TEMPLATES.keys())
