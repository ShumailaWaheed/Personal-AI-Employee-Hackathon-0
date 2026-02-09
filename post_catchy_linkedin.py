"""
Direct LinkedIn post execution for catchy Agentic AI post
"""
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent / 'src'))

from utils.mcp_client import MCPClient
from dotenv import load_dotenv

# Load environment
load_dotenv()

# The catchy LinkedIn post content
post_text = """🚀 The AI Revolution You Didn't See Coming: AGENTIC AI

Forget chatbots. Forget assistants. We're entering the era of AI that ACTS.

🎯 What Makes It Different?

Traditional AI: "Tell me what to do"
Agentic AI: "Let me figure it out and execute"

💡 Real-World Impact:

✅ Customer Support Agent
   → Resolves 80% of queries autonomously
   → Escalates complex cases to humans
   → Learns from every interaction

✅ Personal Workflow Manager
   → Prioritizes your inbox automatically
   → Schedules meetings based on context
   → Executes approved tasks while you sleep

✅ Business Intelligence Analyst
   → Monitors market trends 24/7
   → Generates weekly insights
   → Flags opportunities in real-time

🔥 Why This Matters:

We're shifting from:
❌ AI as a tool you use
✅ AI as a teammate that acts

The companies that adopt Agentic AI first will have an unfair advantage.

🤖 I built my own Agentic AI employee that:
→ Manages my social media (including this post!)
→ Handles approvals autonomously
→ Integrates with 5+ platforms
→ Maintains human-in-the-loop safety

The future isn't about replacing humans.
It's about AI that amplifies human potential.

Are you ready for autonomous intelligence?

#AgenticAI #ArtificialIntelligence #AI #FutureOfWork #Automation #Innovation #MachineLearning #Tech #Productivity #DigitalTransformation"""

def main():
    print("=" * 80)
    print("POSTING CATCHY LINKEDIN POST: Agentic AI")
    print("=" * 80)

    print(f"\nPost length: {len(post_text)} characters")
    print("\nPost contains emojis and formatted content for LinkedIn...")

    # Create MCP client
    client = MCPClient()

    print("\n" + "=" * 80)
    print("EXECUTING LinkedIn Post via MCP...")
    print("=" * 80)

    # Post to LinkedIn
    result = client.create_linkedin_post({'text': post_text})

    print("\n" + "=" * 80)
    if isinstance(result, dict) and result.get('success'):
        print("SUCCESS! CATCHY LINKEDIN POST PUBLISHED!")
        print("=" * 80)
        print(f"\nPost ID: {result.get('post_id', 'unknown')}")
        print(f"Platform: LinkedIn")
        print(f"Account: {os.getenv('LINKEDIN_PERSONAL_ACCOUNT_ID', 'configured')}")
        print("\nThe post is now live on your LinkedIn profile!")
    else:
        print("FAILED TO POST")
        print("=" * 80)
        print(f"Error: {result}")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
