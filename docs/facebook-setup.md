# Facebook API Setup Guide

To enable Facebook posting in your Personal AI Employee, you need an Access Token from Facebook Developer Portal.

## Prerequisites
- Facebook Account
- Facebook Developer Account (free)

## Step-by-Step Guide

### 1. Create Facebook App

1. **Go to Facebook Developers**
   - Visit: https://developers.facebook.com/
   - Click **My Apps** → **Create App**

2. **Choose App Type**
   - Select **Business** or **Consumer**
   - Click **Next**

3. **App Details**
   - **App Name**: "Personal AI Employee" (or your choice)
   - **App Contact Email**: Your email
   - **App Purpose**: Choose appropriate option
   - Click **Create App**

### 2. Configure Facebook Login

1. **Add Facebook Login Product**
   - In your app dashboard, find **Add a Product**
   - Click **Set Up** on **Facebook Login**

2. **Configure OAuth Settings**
   - Go to **Facebook Login** → **Settings**
   - Add to **Valid OAuth Redirect URIs**:
     ```
     https://localhost/
     ```
   - Save changes

### 3. Generate Access Token

#### **Option A: Short-Term Token (For Testing - 1 hour)**

1. Go to **Tools** → **Graph API Explorer**
   - https://developers.facebook.com/tools/explorer/
2. Select your app from dropdown
3. Click **Generate Access Token**
4. Grant permissions:
   - ✅ `pages_manage_posts` (if posting to page)
   - ✅ `publish_to_groups` (if posting to groups)
   - ✅ `pages_read_engagement` (for metrics)
5. Copy the **Access Token**

#### **Option B: Long-Lived Token (60 days)**

After getting short-term token, extend it:

1. Get your **App ID** and **App Secret** from **Settings** → **Basic**

2. Make this API call (replace values):
   ```bash
   curl -X GET "https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=SHORT_TERM_TOKEN"
   ```

3. You'll get a response with `access_token` valid for 60 days

#### **Option C: Never-Expiring Page Access Token**

For posting to Facebook Pages (recommended for business):

1. Get a long-lived User Access Token (Option B)
2. Get your Page ID:
   - Go to your Facebook Page
   - **Settings** → **Page Info**
   - Copy **Page ID**

3. Get Page Access Token:
   ```bash
   curl -X GET "https://graph.facebook.com/v19.0/PAGE_ID?fields=access_token&access_token=LONG_LIVED_USER_TOKEN"
   ```

4. This Page Access Token never expires!

### 4. Update Your .env File

Add to your `.env` file:

```env
# Facebook MCP
FACEBOOK_ACCESS_TOKEN=your-access-token-here
FACEBOOK_PAGE_ID=your-page-id-here  # Optional: for page posting
```

### 5. Test Your Integration

Run the test script:
```bash
python test_facebook.py
```

This will:
1. ✅ Verify credentials are present
2. ✅ Test authentication
3. ✅ Offer to post a test message

---

## Posting Options

### Post to Personal Profile (Timeline)
```env
FACEBOOK_ACCESS_TOKEN=your-user-access-token
# No FACEBOOK_PAGE_ID needed
```

In task file:
```markdown
Post on Facebook:

"Your message here"
```

### Post to Facebook Page
```env
FACEBOOK_ACCESS_TOKEN=your-page-access-token
FACEBOOK_PAGE_ID=your-page-id
```

In task file:
```markdown
Post on Facebook page:

"Your message here"
```

---

## Required Permissions

For posting, your app needs these permissions:

| Permission | Purpose | Required For |
|------------|---------|--------------|
| `pages_manage_posts` | Post to pages | Page posting |
| `pages_read_engagement` | Read metrics | Post analytics |
| `publish_to_groups` | Post to groups | Group posting |

---

## Common Issues

### "Invalid OAuth access token"
- Token expired (short-term tokens last 1 hour)
- Regenerate token or use long-lived/page token

### "Permissions error"
- App doesn't have required permissions
- Regenerate token with correct permissions

### "User request limit reached"
- Free tier has rate limits
- Wait or upgrade to Business verification

### Posts not appearing
- Check Privacy settings (posts might be private)
- Verify Page is published (not draft)
- Check for content policy violations

---

## Rate Limits

**Standard Access** (Free):
- 200 calls per hour per user
- 4,800 calls per day

**Business Verification** unlocks higher limits.

---

## Security Notes

1. **NEVER** commit tokens to version control
2. `.env` is in `.gitignore` (already configured)
3. Use Page Access Tokens for production (never expire)
4. User tokens expire - not suitable for automation
5. Rotate tokens periodically

---

## Token Hierarchy

```
App Access Token (App-level)
└─ User Access Token (1 hour)
   └─ Long-Lived User Token (60 days)
      └─ Page Access Token (never expires) ← Best for automation
```

---

## Resources

- [Facebook Graph API Documentation](https://developers.facebook.com/docs/graph-api/)
- [Access Token Guide](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/)
- [Publishing to Pages](https://developers.facebook.com/docs/pages-api/publishing/)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
