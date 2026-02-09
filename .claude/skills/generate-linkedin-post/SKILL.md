# Generate LinkedIn Post

Generate LinkedIn post content and route through HITL approval before publishing.

## Description
This skill generates LinkedIn post drafts based on a given topic, applies rate limiting (1-3 posts/day), and routes the draft through the HITL approval workflow. Posts are generated using templates informed by Company_Handbook.md. The skill enforces LinkedIn rate limits and tracks post performance after publishing.

## When to Use
- User or system wants to create a LinkedIn post
- Content marketing tasks reference social media or LinkedIn
- Action files mention "post", "publish", "share", or "LinkedIn"
- Scheduled content generation is triggered

## Inputs
- **topic** (required): Subject of the post (e.g., "AI Innovation", "Q1 Results")
- **style** (optional): One of `professional`, `thought_leadership`, `engagement` (default: professional)
- `AI_Employee_Vault/Company_Handbook.md` for business context

## Outputs
- Approval request in `AI_Employee_Vault/Pending_Approval/` with the post draft
- Rate limiter state updated in `AI_Employee_Vault/Logs/.rate_limiter_state.json`
- Post tracked in `AI_Employee_Vault/Logs/post_performance.json` after execution

## Approval Required
- **Always yes** - LinkedIn posts always require HITL approval

## MCP Servers Used
- `linkedin_mcp` (future) - For actual posting after approval
- Currently executes in DRY_RUN mode

## Rate Limiting
- Maximum **3 posts per day** (configurable)
- Counter resets at midnight
- If limit reached, skill refuses to generate and reports remaining count
- State persisted in `AI_Employee_Vault/Logs/.rate_limiter_state.json`

## Available Styles

### professional
```
Excited to share insights on [topic].

Key takeaways:
- Innovation drives growth
- Collaboration creates value
- Continuous learning is essential

What are your thoughts on this topic?
```

### thought_leadership
```
The landscape of [topic] is evolving rapidly.

Here are three trends I'm watching:
1. Increasing automation and AI integration
2. Shift towards sustainable practices
3. Growing importance of data-driven decisions

How is your organization adapting?
```

### engagement
```
Quick question for my network:

How are you approaching [topic] in your work?

I'd love to hear different perspectives.
```

## Content Templates
Four template types available in `src/social/content_templates.py`:
- **company_update**: Hook → Details → CTA
- **industry_insight**: Observation → Analysis → Question
- **milestone**: Achievement → Context → Gratitude
- **tip_share**: Problem → Solution → Benefit

## Process Steps
1. Check rate limiter - abort if daily limit reached
2. Load Company_Handbook.md for business context
3. Generate post content based on topic + style
4. Suggest relevant hashtags
5. Create approval request in /Pending_Approval
6. On approval: record post, update rate limiter, track performance

## Code Reference
- `src/social/linkedin_post_generator.py` - LinkedInPostGenerator
- `src/social/content_templates.py` - Template definitions
- `src/social/rate_limiter.py` - RateLimiter
- `src/social/performance_tracker.py` - PerformanceTracker
- `src/workflows/linkedin_approval_flow.py` - LinkedInApprovalFlow

## Quality Criteria
- Rate limits are enforced (never exceed 3/day)
- All posts go through HITL approval (no auto-posting)
- Hashtags are relevant to the topic
- Content aligns with Company_Handbook.md tone
- Post performance is tracked after publishing

## Related Skills
- `hitl-approval` - Posts are always routed through HITL
- `audit-log` - Post creation and execution are logged
- `update-dashboard` - Dashboard reflects post status
