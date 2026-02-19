# Social Media Post

Execute multi-platform social media posts via MCP servers after HITL approval.

## Description
This skill handles posting content to multiple social media platforms: LinkedIn, Facebook, Twitter/X, Instagram, and WhatsApp. All posts require HITL approval before publishing (no auto-posting). Each platform has its own MCP server for execution. The skill extracts post content from approved action files, routes to the correct platform MCP, and logs results. Instagram posts support image attachments.

## When to Use
- An approved social media action exists in `/Approved/`
- User creates an action item requesting a social media post
- Scheduled content publishing is triggered
- Multi-platform cross-posting is requested

## Inputs
- Approved action file from `AI_Employee_Vault/Approved/` with platform and content details
- Or action file from `/Needs_Action/` (will be routed through HITL first)

## Outputs
- Post published on target platform via MCP
- Audit log entry with post result and platform-specific ID
- Action file moved to `/Done/`
- On failure: entry added to retry queue

## Approval Required
- **Always yes** — social media posts always require HITL approval
- Posts are classified as `medium` risk by `detect-sensitive-action`

## Supported Platforms & MCP Servers

| Platform | MCP Server | Method | Key Parameter |
|----------|-----------|--------|---------------|
| LinkedIn | `linkedin_mcp` (`mcp/linkedin_server.py`) | `create_post` | `text` |
| Facebook | `facebook_mcp` (`mcp/facebook_server.py`) | `create_post` | `message` |
| Twitter/X | `twitter_mcp` (`mcp/twitter_server.py`) | `create_tweet` | `text` |
| Instagram | `instagram_mcp` (`mcp/instagram_server.py`) | `create_post` | `caption` + `image_url` |
| WhatsApp | `whatsapp_mcp` (`mcp/whatsapp_server.py`) | `send_message` | `to` + `message` |

## Action Type Detection
From `detect-sensitive-action` skill:

| Content Contains | Action Type |
|-----------------|-------------|
| linkedin, post, publish | `linkedin_post` |
| facebook, fb | `facebook_post` |
| twitter, tweet, x.com | `twitter_post` |
| instagram, ig, insta | `instagram_post` |
| whatsapp, message, chat | `whatsapp_message` |

## Content Extraction

### Post Text
The Gold processor extracts post content in this order:
1. Quoted text between `"..."` in the action file
2. Content after frontmatter headers
3. Full body text as fallback

### Draft Reply (WhatsApp)
For WhatsApp messages, the `## Draft Reply` section is preferred:
```markdown
## Draft Reply
Hi, thanks for reaching out! I'll get back to you shortly.
```

### Image URL (Instagram)
Extracted from frontmatter `image_url:` field or Markdown image syntax `![alt](url)`.

## Process Steps

### 1. Detection & Classification
1. File arrives in `/Needs_Action/`
2. `detect-sensitive-action` identifies it as social media (medium risk)
3. `classify-priority-domain` assigns priority and domain

### 2. Approval Routing
1. Gold processor routes to `/Pending_Approval/`
2. Approval file created with draft content and target platform
3. Human reviews and moves to `/Approved/` or `/Rejected/`

### 3. Execution
1. Gold processor detects approved file
2. `_execute_via_mcp()` identifies the action type
3. Content extracted via `_extract_post_text()` (or `_extract_draft_reply()` for WhatsApp)
4. MCP client calls the appropriate server:
   - LinkedIn: `mcp_client.create_linkedin_post({'text': text})`
   - Facebook: `mcp_client.create_facebook_post({'message': text})`
   - Twitter: `mcp_client.create_tweet({'text': text})`
   - Instagram: `mcp_client.create_instagram_post({'caption': text, 'image_url': url})`
   - WhatsApp: `mcp_client.send_whatsapp({'to': target, 'message': message})`
5. Result logged (success with post_id, or failure)
6. On success: file moved to `/Done/`
7. On failure: entry added to retry queue

### 4. DRY_RUN Mode
When `DRY_RUN=true`, the system logs the intent without calling MCP:
```
(DRY RUN) Would execute: task_post_update.md
```

## Environment Variables
```
# LinkedIn
LINKEDIN_ACCESS_TOKEN=your-token
LINKEDIN_PERSONAL_ACCOUNT_ID=your-id

# Facebook
FACEBOOK_ACCESS_TOKEN=your-token
FACEBOOK_PAGE_ID=your-page-id

# Twitter/X
TWITTER_API_KEY=your-key
TWITTER_API_SECRET=your-secret
TWITTER_ACCESS_TOKEN=your-token
TWITTER_ACCESS_TOKEN_SECRET=your-secret

# Instagram
INSTAGRAM_MODE=playwright        # or api
INSTAGRAM_ACCESS_TOKEN=your-token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your-id

# WhatsApp
WHATSAPP_MODE=playwright
WHATSAPP_API_TOKEN=your-token
```

## MCP Client Methods
Available in `src/utils/mcp_client.py`:

| Method | Platform | Returns |
|--------|----------|---------|
| `create_linkedin_post(params)` | LinkedIn | `{success, post_id}` |
| `create_facebook_post(params)` | Facebook | `{success, post_id}` |
| `create_tweet(params)` | Twitter | `{success, tweet_id}` |
| `create_instagram_post(params)` | Instagram | `{success, post_id}` |
| `send_whatsapp(params)` | WhatsApp | `{success}` |
| `get_linkedin_metrics(params)` | LinkedIn | Engagement data |
| `get_facebook_post_metrics(params)` | Facebook | Engagement data |
| `get_tweet_metrics(params)` | Twitter | Engagement data |
| `get_instagram_post_metrics(params)` | Instagram | Engagement data |

## Code Reference
- `src/processors/gold_processor.py` — `_execute_via_mcp()` (platform routing), `_extract_post_text()`, `_extract_draft_reply()`, `_extract_image_url()`
- `src/utils/mcp_client.py` — Platform-specific methods (create_linkedin_post, create_tweet, etc.)
- `mcp/linkedin_server.py` — LinkedIn MCP server
- `mcp/facebook_server.py` — Facebook MCP server
- `mcp/twitter_server.py` — Twitter MCP server
- `mcp/instagram_server.py` — Instagram MCP server
- `mcp/whatsapp_server.py` — WhatsApp MCP server
- `src/social/linkedin_post_generator.py` — LinkedIn content generation (from existing skill)
- `src/social/content_templates.py` — Post templates

## Quality Criteria
- All social posts go through HITL approval (no auto-posting)
- Platform-specific parameters are correctly mapped (text vs message vs caption)
- Instagram posts include image_url when available
- WhatsApp messages prefer draft reply over generic extraction
- DRY_RUN mode prevents actual posting
- Failed posts enter the retry queue (not silently dropped)
- Post IDs are logged on success for tracking

## Related Skills
- `generate-linkedin-post` — LinkedIn-specific content generation with templates and rate limiting
- `hitl-approval` — All social posts routed through HITL
- `detect-sensitive-action` — Classifies social media actions as medium risk
- `retry-failed-action` — Handles failed platform API calls
- `audit-log` — Logs all post attempts and results
