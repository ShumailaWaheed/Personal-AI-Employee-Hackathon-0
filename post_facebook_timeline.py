"""
Post to Facebook timeline via MCP
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / 'src'))

from utils.mcp_client import MCPClient

def main():
    print("=" * 80)
    print("FACEBOOK TIMELINE POST")
    print("=" * 80)

    # Facebook post content
    post_message = """Building an autonomous AI agent that manages my workflow - from inbox triage to social media posting - all with human-in-the-loop safety.

The future of productivity is agentic AI working alongside you.

#AI #AgenticAI #Automation #Innovation"""

    print(f"\nPost text:")
    print(f"{post_message}")
    print(f"\nLength: {len(post_message)} characters")

    # Create MCP client
    client = MCPClient()

    print("\n" + "=" * 80)
    print("POSTING TO FACEBOOK TIMELINE...")
    print("=" * 80)

    # Post to Facebook
    result = client.create_facebook_post({'message': post_message})

    print("\n" + "=" * 80)
    if isinstance(result, dict) and result.get('success'):
        print("SUCCESS! FACEBOOK POST PUBLISHED!")
        print("=" * 80)
        post_id = result.get('post_id', 'unknown')
        print(f"\nPost ID: {post_id}")
        print(f"Account: Alisha Naz")
        print("\nYour post is now live on your Facebook timeline!")
        print("Check your Facebook to see it!")
        return 0
    else:
        print("FAILED TO POST")
        print("=" * 80)
        print(f"Error: {result}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
