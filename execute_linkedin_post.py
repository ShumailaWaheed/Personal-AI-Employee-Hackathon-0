"""
Quick script to execute the catchy LinkedIn post directly
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / 'src'))

from processors.gold_processor import GoldProcessor
from utils.config_loader import load_config
from utils.logger import setup_logger

def main():
    config = load_config()
    setup_logger(config['LOG_LEVEL'])

    processor = GoldProcessor(config['VAULT_PATH'], config)

    # Read the catchy post
    task_file = Path('AI_Employee_Vault/Needs_Action/task_linkedin_catchy_agentic.md')

    if not task_file.exists():
        print(f"Task file not found: {task_file}")
        return

    content = task_file.read_text(encoding='utf-8')
    print(f"Processing: {task_file.name}")

    # Extract the post text
    text = processor._extract_post_text(content)
    print(f"\nPost preview (first 200 chars):\n{text[:200]}...\n")

    # Execute via MCP
    print("Posting to LinkedIn...")
    result = processor.mcp_client.create_linkedin_post({'text': text})

    if isinstance(result, dict) and result.get('success'):
        print(f"\n✅ SUCCESS! LinkedIn post published!")
        print(f"Post ID: {result.get('post_id', 'unknown')}")

        # Move to Done
        done_file = Path('AI_Employee_Vault/Done') / task_file.name
        task_file.rename(done_file)
        print(f"Task moved to Done: {done_file.name}")
    else:
        print(f"\n❌ FAILED: {result}")

if __name__ == "__main__":
    main()
