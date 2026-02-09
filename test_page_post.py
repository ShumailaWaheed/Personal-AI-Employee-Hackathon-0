"""
Test posting to Facebook Page directly
"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
page_id = os.getenv('FACEBOOK_PAGE_ID')

print("=" * 80)
print("TESTING FACEBOOK PAGE POST")
print("=" * 80)

print(f"\nPage ID: {page_id}")
print(f"Access Token: {access_token[:30]}...")

# Try posting to the page
print("\n" + "=" * 80)
print("POSTING TO PAGE")
print("=" * 80)

url = f'https://graph.facebook.com/v19.0/{page_id}/feed'
payload = {
    'message': 'Testing Facebook Page integration for Personal AI Employee! This is an automated post from my AI assistant. #AI #Automation',
    'access_token': access_token,
}

resp = requests.post(url, data=payload)

print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")

if resp.status_code == 200:
    data = resp.json()
    post_id = data.get('id', 'unknown')
    print("\n" + "=" * 80)
    print("SUCCESS! POST PUBLISHED TO FACEBOOK PAGE!")
    print("=" * 80)
    print(f"\nPost ID: {post_id}")
    print(f"Page ID: {page_id}")
    print("\nCheck your Facebook Page to see the post!")
else:
    print("\n" + "=" * 80)
    print("ERROR DETAILS")
    print("=" * 80)
    try:
        error_data = resp.json()
        error_msg = error_data.get('error', {})
        print(f"Error Type: {error_msg.get('type', 'unknown')}")
        print(f"Error Message: {error_msg.get('message', 'unknown')}")
        print(f"Error Code: {error_msg.get('code', 'unknown')}")

        if 'OAuthException' in error_msg.get('type', ''):
            print("\n*** TOKEN ISSUE ***")
            print("You need a PAGE Access Token, not a User Access Token")
            print("\nSteps to fix:")
            print("1. Go to: https://developers.facebook.com/tools/explorer/")
            print("2. Click 'User or Page' dropdown")
            print("3. Select 'Get Page Access Token' (NOT User Access Token)")
            print("4. Choose your page: Page ID 61579018679106")
            print("5. Grant permissions: pages_read_engagement, pages_manage_posts")
            print("6. Copy the NEW token and update .env file")
    except:
        pass
