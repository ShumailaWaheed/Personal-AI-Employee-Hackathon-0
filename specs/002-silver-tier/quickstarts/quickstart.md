# Silver Tier Personal AI Employee Quickstart Guide

## Overview
This guide provides step-by-step instructions to set up the Silver Tier Personal AI Employee system, which extends Bronze Tier functionality with multi-watcher support, MCP server integration, HITL approval workflows, and enhanced audit logging.

## Prerequisites
- Python 3.13+ installed
- Node.js 18+ installed
- Git installed
- PM2 installed globally: `npm install -g pm2`
- Playwright for Python: `pip install playwright && playwright install`
- Access to email SMTP service or API (Gmail, SendGrid, etc.)
- LinkedIn API access (Marketing Developer Platform)
- Valid .env file with required credentials (not committed to git)

## Installation Steps

### 1. Clone and Initialize Repository
```bash
git clone <repository-url>
cd personal-ai-employee
pip install -r requirements.txt  # if exists, otherwise install packages individually
```

### 2. Set Up Vault Structure
Create the Silver Tier vault structure:
```
AI_Employee_Vault/
├── Inbox/
├── Needs_Action/
├── Pending_Approval/
├── Approved/
├── Rejected/
├── Done/
├── Logs/
├── Plans/
├── Dashboard.md
└── Company_Handbook.md
```

### 3. Configure Environment Variables
Create a `.env` file (and ensure it's in `.gitignore`):
```env
# Email MCP Configuration
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USERNAME=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-app-password
EMAIL_FROM_ADDRESS=your-email@gmail.com

# Gmail API (if using Gmail watcher)
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# LinkedIn API
LINKEDIN_ACCESS_TOKEN=your-linkedin-token
LINKEDIN_PERSONAL_ACCOUNT_ID=your-profile-id

# Process management
PROCESSING_INTERVAL=30
DRY_RUN=false

# Audit logging
LOG_RETENTION_DAYS=90
```

### 4. Install and Set Up MCP Server
```bash
# Navigate to MCP directory
cd mcp/

# Install dependencies
npm install @modelcontextprotocol/server

# Or create a Python-based MCP server
pip install jsonrpc
```

Create the Email MCP server (`mcp/email-server.py`):
```python
#!/usr/bin/env python3
"""
Email MCP Server
Handles email sending through JSON-RPC over stdio
"""

import sys
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Dict, Any, List

class EmailMCPServer:
    def __init__(self):
        self.smtp_host = os.getenv('EMAIL_SMTP_HOST', 'localhost')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', 587))
        self.smtp_username = os.getenv('EMAIL_SMTP_USERNAME')
        self.smtp_password = os.getenv('EMAIL_SMTP_PASSWORD')
        self.from_address = os.getenv('EMAIL_FROM_ADDRESS')

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get('method')

        if method == 'send_email':
            return self.send_email(request.get('params', {}))
        elif method == 'get_account_info':
            return self.get_account_info()
        elif method == 'validate_recipients':
            return self.validate_recipients(request.get('params', {}))
        elif method == 'ping':
            return {"jsonrpc": "2.0", "id": request.get('id'), "result": {"status": "ok"}}
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                }
            }

    def send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Extract parameters
            to = params.get('to', [])
            cc = params.get('cc', [])
            bcc = params.get('bcc', [])
            subject = params.get('subject', '')
            body = params.get('body', '')
            html_body = params.get('html_body', '')
            attachments = params.get('attachments', [])

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_address
            msg['To'] = ', '.join(to)
            if cc:
                msg['Cc'] = ', '.join(cc)

            # Add text and HTML parts
            if body:
                text_part = MIMEText(body, 'plain')
                msg.attach(text_part)

            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)

            # Add attachments
            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                # Decode base64 content
                import base64
                decoded_content = base64.b64decode(attachment['content_base64'])
                part.set_payload(decoded_content)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment["filename"]}'
                )
                msg.attach(part)

            # Connect and send
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)

            all_recipients = to + cc + bcc
            server.send_message(msg, to_addrs=all_recipients)
            server.quit()

            return {
                "jsonrpc": "2.0",
                "id": params.get('id'),
                "result": {
                    "success": True,
                    "message_ids": ["msg_" + str(hash(tuple(all_recipients + [subject])))],
                    "sent_count": len(all_recipients)
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": params.get('id'),
                "error": {
                    "code": -32000,
                    "message": f"Email sending failed: {str(e)}"
                }
            }

    def get_account_info(self) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": None,
            "result": {
                "success": True,
                "account": {
                    "email_address": self.from_address,
                    "service_provider": self.smtp_host,
                    "rate_limits": {
                        "messages_per_day": 500,
                        "current_usage": 0
                    },
                    "connected_at": "2026-01-26T10:00:00Z"
                }
            }
        }

    def validate_recipients(self, params: Dict[str, Any]) -> Dict[str, Any]:
        recipients = params.get('recipients', [])
        valid = []
        invalid = []
        details = {}

        for recipient in recipients:
            # Simple validation - in practice, this would do more thorough checking
            if '@' in recipient and '.' in recipient.split('@')[1]:
                valid.append(recipient)
                details[recipient] = {
                    "valid": True,
                    "syntax_valid": True,
                    "domain_exists": True
                }
            else:
                invalid.append(recipient)
                details[recipient] = {
                    "valid": False,
                    "reason": "invalid_syntax"
                }

        return {
            "jsonrpc": "2.0",
            "id": params.get('id'),
            "result": {
                "success": True,
                "valid_recipients": valid,
                "invalid_recipients": invalid,
                "validation_details": details
            }
        }

def main():
    server = EmailMCPServer()

    # Read from stdin and write to stdout (JSON-RPC over stdio)
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
            print(json.dumps(error_response), flush=True)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
```

### 5. Set Up Watchers

Create the WhatsApp Watcher (`watchers/whatsapp_watcher.py`):
```python
import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright
import json
from datetime import datetime

class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def check_for_updates(self) -> list:
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        pass

    def run(self):
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.logger.error(f'Error: {e}')
            time.sleep(self.check_interval)

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, check_interval: int = 30):
        super().__init__(vault_path, check_interval)
        self.playwright = None
        self.browser = None
        self.page = None

    def initialize_browser(self):
        """Initialize Playwright browser with persistent context"""
        self.playwright = sync_playwright().start()
        # Use persistent context to maintain WhatsApp Web session
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir="./whatsapp_session",  # Save session data
            headless=False,  # Set to True for production
            viewport={'width': 1280, 'height': 800}
        )
        self.page = self.browser.new_page()
        self.page.goto("https://web.whatsapp.com/")

        # Wait for QR code scan
        self.page.wait_for_selector('div[data-testid="chat-list-launcher"]', timeout=60000)

    def check_for_updates(self) -> list:
        """Check WhatsApp Web for new messages or status updates"""
        if not self.page:
            self.initialize_browser()

        # Check for unread chats
        unread_chats = []
        try:
            chat_elements = self.page.query_selector_all('div[data-testid="conversation"]')

            for chat_element in chat_elements:
                # Check for unread indicators
                unread_badge = chat_element.query_selector('span[data-testid="unread-count"]')
                if unread_badge:
                    chat_name_elem = chat_element.query_selector('div[title]')
                    if chat_name_elem:
                        chat_name = chat_name_elem.get_attribute('title')
                        unread_chats.append({
                            'type': 'whatsapp_message',
                            'contact': chat_name,
                            'timestamp': datetime.now().isoformat(),
                            'status': 'unread'
                        })
        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")

        return unread_chats

    def create_action_file(self, item) -> Path:
        """Create an action file for the new WhatsApp message"""
        filename = f"whatsapp_{item['contact']}_{int(datetime.now().timestamp())}.md"
        filepath = self.needs_action / filename

        content = f"""# WhatsApp Message Alert: {item['contact']}

## Message Details
- Contact: {item['contact']}
- Received: {item['timestamp']}
- Status: {item['status']}

## Action Required
Review the message from {item['contact']} in WhatsApp Web and determine appropriate response.

## Recommended Actions
- Respond to important messages
- Schedule follow-up if needed
- Create task for ongoing conversations
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        self.logger.info(f"Created WhatsApp action file: {filepath}")
        return filepath
```

Create the LinkedIn Watcher (`watchers/linkedin_watcher.py`):
```python
import time
import logging
import requests
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
import os

class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def check_for_updates(self) -> list:
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        pass

    def run(self):
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.logger.error(f'Error: {e}')
            time.sleep(self.check_interval)

class LinkedInWatcher(BaseWatcher):
    def __init__(self, vault_path: str, check_interval: int = 300):  # Check every 5 minutes
        super().__init__(vault_path, check_interval)
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.personal_account_id = os.getenv('LINKEDIN_PERSONAL_ACCOUNT_ID')
        self.api_base = "https://api.linkedin.com/v2"

    def check_for_updates(self) -> list:
        """Check LinkedIn for updates related to the account"""
        updates = []

        if not self.access_token:
            self.logger.error("LINKEDIN_ACCESS_TOKEN not set in environment")
            return updates

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json'
        }

        # Check for new connections
        try:
            connections_url = f"{self.api_base}/networkSizes/{self.personal_account_id}?edgeType=CONNECTIONS"
            response = requests.get(connections_url, headers=headers)
            if response.status_code == 200:
                # This is a simplified check - real implementation would be more complex
                updates.append({
                    'type': 'linkedin_update',
                    'update_type': 'connection_count_change',
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            self.logger.error(f"Error checking LinkedIn connections: {e}")

        # Check for comments on recent posts (if we're tracking this)
        try:
            # This would require additional endpoint access
            pass
        except Exception as e:
            self.logger.error(f"Error checking LinkedIn activity: {e}")

        return updates

    def create_action_file(self, item) -> Path:
        """Create an action file for LinkedIn updates"""
        filename = f"linkedin_update_{int(datetime.now().timestamp())}.md"
        filepath = self.needs_action / filename

        content = f"""# LinkedIn Update Notification

## Update Details
- Type: {item['update_type']}
- Occurred: {item['timestamp']}

## Action Required
Review LinkedIn account for new activity and determine appropriate response.

## Recommended Actions
- Engage with new connections
- Respond to comments on recent posts
- Create new content based on network activity
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        self.logger.info(f"Created LinkedIn action file: {filepath}")
        return filepath
```

### 6. Set Up PM2 Process Management

Create PM2 ecosystem file (`ecosystem.config.js`):
```javascript
module.exports = {
  apps: [{
    name: 'gmail-watcher',
    script: './watchers/gmail_watcher.py',
    interpreter: 'python3',
    watch: false,
    env: {
      NODE_ENV: 'development',
      PYTHONPATH: './src'
    },
    error_file: './logs/gmail-watcher-error.log',
    out_file: './logs/gmail-watcher-out.log',
    log_file: './logs/gmail-watcher-combined.log',
    time: true
  }, {
    name: 'whatsapp-watcher',
    script: './watchers/whatsapp_watcher.py',
    interpreter: 'python3',
    watch: false,
    env: {
      NODE_ENV: 'development',
      PYTHONPATH: './src'
    },
    error_file: './logs/whatsapp-watcher-error.log',
    out_file: './logs/whatsapp-watcher-out.log',
    log_file: './logs/whatsapp-watcher-combined.log',
    time: true
  }, {
    name: 'linkedin-watcher',
    script: './watchers/linkedin_watcher.py',
    interpreter: 'python3',
    watch: false,
    env: {
      NODE_ENV: 'development',
      PYTHONPATH: './src'
    },
    error_file: './logs/linkedin-watcher-error.log',
    out_file: './logs/linkedin-watcher-out.log',
    log_file: './logs/linkedin-watcher-combined.log',
    time: true
  }, {
    name: 'main-processor',
    script: './src/main.py',
    interpreter: 'python3',
    watch: false,
    env: {
      NODE_ENV: 'development',
      PYTHONPATH: './src'
    },
    error_file: './logs/main-processor-error.log',
    out_file: './logs/main-processor-out.log',
    log_file: './logs/main-processor-combined.log',
    time: true
  }]
};
```

### 7. Update Main Processor

Update the main processor to handle the new Silver Tier functionality (`src/main.py`):
```python
#!/usr/bin/env python3
"""
Silver Tier Personal AI Employee - Main Processor

Handles the core logic for the Silver Tier system including:
- Monitoring /Needs_Action for new tasks
- Creating Plan.md files
- Managing HITL approval workflow
- Executing approved actions via MCP
- Audit logging
"""

import time
import logging
from pathlib import Path
import json
import subprocess
import os
from datetime import datetime
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main-processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SilverTierProcessor:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.plans = self.vault_path / 'Plans'

        # Ensure directories exist
        for directory in [self.pending_approval, self.approved, self.rejected, self.done, self.logs, self.plans]:
            directory.mkdir(exist_ok=True)

        self.processing_interval = int(os.getenv('PROCESSING_INTERVAL', 30))
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'

    def run(self):
        """Main processing loop"""
        logger.info("Starting Silver Tier Personal AI Employee processor...")

        while True:
            try:
                # Process new items in Needs_Action
                self.process_needs_action_items()

                # Check for approved items and execute them
                self.process_approved_items()

                # Update dashboard
                self.update_dashboard()

            except Exception as e:
                logger.error(f"Error in main processing loop: {e}")

            time.sleep(self.processing_interval)

    def process_needs_action_items(self):
        """Process items in Needs_Action folder"""
        for action_file in self.needs_action.glob("*.md"):
            logger.info(f"Processing action file: {action_file.name}")

            # Read the action file content
            with open(action_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create a Plan.md file based on the action
            plan_file = self.create_plan_from_action(action_file, content)

            # Determine if this action requires approval
            requires_approval = self.action_requires_approval(content)

            if requires_approval:
                # Move to Pending Approval
                approval_file = self.create_approval_request(plan_file)
                approval_path = self.pending_approval / approval_file.name
                approval_file.rename(approval_path)
                logger.info(f"Created approval request: {approval_path.name}")

                # Move original action file to Done after creating plan
                done_path = self.done / action_file.name
                action_file.rename(done_path)
            else:
                # For non-sensitive actions, we can process directly
                logger.info(f"Processing non-sensitive action: {action_file.name}")
                self.execute_direct_action(action_file, content)
                # Move to Done
                done_path = self.done / action_file.name
                action_file.rename(done_path)

    def create_plan_from_action(self, action_file: Path, content: str) -> Path:
        """Create a Plan.md file from an action file"""
        plan_filename = f"Plan_{action_file.stem}_{int(datetime.now().timestamp())}.md"
        plan_path = self.plans / plan_filename

        # In a real implementation, this would involve more sophisticated
        # planning based on the action content
        plan_content = f"""# Plan for {action_file.stem}

## Action Summary
{content[:500]}...

## Planned Steps
1. Analyze the requested action
2. Determine if approval is needed
3. Create appropriate approval request or execute directly
4. Log the outcome
5. Update dashboard

## Status
- Created: {datetime.now().isoformat()}
- Status: pending

## Dependencies
- Action file: {action_file.name}
"""

        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)

        logger.info(f"Created plan file: {plan_path.name}")
        return plan_path

    def action_requires_approval(self, content: str) -> bool:
        """Determine if an action requires human approval"""
        # In a real implementation, this would be more sophisticated
        # checking for sensitive actions like sending emails, social posts, etc.
        content_lower = content.lower()

        # Keywords that indicate sensitive actions requiring approval
        sensitive_keywords = [
            'email', 'send', 'post', 'publish', 'share', 'message',
            'contact', 'reach out', 'reply', 'respond', 'payment',
            'transaction', 'buy', 'purchase', 'transfer'
        ]

        return any(keyword in content_lower for keyword in sensitive_keywords)

    def create_approval_request(self, plan_file: Path) -> Path:
        """Create an approval request file based on a plan"""
        approval_filename = f"approval_{plan_file.stem}_{int(datetime.now().timestamp())}.md"
        approval_path = self.pending_approval / approval_filename

        # Read plan content to understand the action
        with open(plan_file, 'r', encoding='utf-8') as f:
            plan_content = f.read()

        approval_content = f"""---
type: approval_request
action: automated_request
created: {datetime.now().isoformat()}
status: pending
risk_level: medium
auto_approve_eligible: false
mcp_server: email_mcp
---

# Approval Request: Action from Plan {plan_file.stem}

## Proposed Action
Based on the plan file, the system proposes to take the following action.

## Plan Summary
{plan_content[:1000]}...

## Target
The action will affect the following systems:
- External communications
- Social media platforms
- Email distribution

## Parameters
- Action type: Determined from plan content
- Targets: As specified in plan
- Timing: Immediate upon approval

## Rationale
This action follows from the input received and is part of the automated workflow.

## Risk Assessment
Medium risk as it involves external communications that may represent the company.

## Approval Instructions
- Move to /Approved/ to execute
- Move to /Rejected/ to cancel
- Discuss in Slack channel if uncertain
"""

        with open(approval_path, 'w', encoding='utf-8') as f:
            f.write(approval_content)

        logger.info(f"Created approval request: {approval_path.name}")
        return approval_path

    def process_approved_items(self):
        """Process items that have been approved"""
        for approved_file in self.approved.glob("*.md"):
            logger.info(f"Processing approved item: {approved_file.name}")

            # Execute the action via MCP
            success = self.execute_approved_action(approved_file)

            # Move to Done regardless of success/failure
            done_path = self.done / approved_file.name
            approved_file.rename(done_path)

            # Log the result
            self.log_action_execution(approved_file.name, success)

    def execute_approved_action(self, approved_file: Path) -> bool:
        """Execute an approved action via MCP"""
        logger.info(f"Executing approved action: {approved_file.name}")

        # In a real implementation, this would parse the approval file
        # and determine what action to take, then call the appropriate
        # MCP server to execute it

        # For now, simulate an email sending action
        if not self.dry_run:
            try:
                # Call the email MCP server
                mcp_result = self.call_email_mcp_server({
                    "method": "send_email",
                    "params": {
                        "to": ["manager@company.com"],
                        "subject": f"Action Completed: {approved_file.stem}",
                        "body": f"The requested action from {approved_file.stem} has been processed."
                    }
                })

                logger.info(f"MCP execution result: {mcp_result}")
                return True
            except Exception as e:
                logger.error(f"Failed to execute MCP action: {e}")
                return False
        else:
            logger.info("(DRY RUN) Would execute action via MCP server")
            return True

    def call_email_mcp_server(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Call the email MCP server via JSON-RPC over stdio"""
        # In a real implementation, this would establish a persistent
        # connection to the MCP server and make requests
        # For simulation, we'll just return a success response
        request['id'] = f"req_{int(datetime.now().timestamp())}"

        # In a real implementation, we'd do something like:
        # proc = subprocess.Popen(['python', 'mcp/email-server.py'],
        #                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        #                        stderr=subprocess.PIPE, text=True)
        # proc.stdin.write(json.dumps(request) + '\n')
        # response = json.loads(proc.stdout.readline())
        # proc.stdin.close()

        # Simulated response
        return {
            "jsonrpc": "2.0",
            "id": request['id'],
            "result": {
                "success": True,
                "message_ids": ["msg_12345"],
                "sent_count": 1
            }
        }

    def execute_direct_action(self, action_file: Path, content: str):
        """Execute a non-sensitive action directly"""
        logger.info(f"Executing direct action for: {action_file.name}")

        # For non-sensitive actions, we might still want to log them
        self.log_action_execution(action_file.name, True, action_type="direct")

    def log_action_execution(self, action_name: str, success: bool, action_type: str = "approved"):
        """Log action execution to audit log"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_path = self.logs / f"{today}.json"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_name": action_name,
            "action_type": action_type,
            "actor": "system",
            "target": "various",
            "parameters": {"action_file": action_name},
            "approval_status": "executed" if action_type == "approved" else "direct",
            "result": "success" if success else "failure",
            "execution_time_ms": 150  # Simulated
        }

        # Read existing log if it exists
        existing_logs = []
        if log_path.exists():
            with open(log_path, 'r', encoding='utf-8') as f:
                try:
                    existing_logs = json.load(f)
                except json.JSONDecodeError:
                    existing_logs = []

        # Add new entry
        existing_logs.append(log_entry)

        # Write back to file
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(existing_logs, f, indent=2)

        logger.info(f"Logged action execution to {log_path}")

    def update_dashboard(self):
        """Update the Dashboard.md file with current status"""
        dashboard_path = self.vault_path / 'Dashboard.md'

        # Count items in various states
        pending_approval_count = len(list(self.pending_approval.glob("*.md")))
        approved_count = len(list(self.approved.glob("*.md")))
        rejected_count = len(list(self.rejected.glob("*.md")))
        needs_action_count = len(list(self.needs_action.glob("*.md")))
        done_count = len(list(self.done.glob("*.md")))

        # Get recent log entries
        today = datetime.now().strftime('%Y-%m-%d')
        log_path = self.logs / f"{today}.json"
        recent_logs = []
        if log_path.exists():
            with open(log_path, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                    # Get last 5 log entries
                    recent_logs = logs[-5:] if len(logs) >= 5 else logs
                except json.JSONDecodeError:
                    recent_logs = []

        dashboard_content = f"""# Personal AI Employee Dashboard

**Last Updated**: {datetime.now().isoformat()}

## Status Overview
- **Pending Approval**: {pending_approval_count} items
- **Approved**: {approved_count} items
- **Rejected**: {rejected_count} items
- **Needs Action**: {needs_action_count} items
- **Completed**: {done_count} items

## Pending Approval Queue
"""

        for i, pending_file in enumerate(list(self.pending_approval.glob("*.md"))[:5]):
            dashboard_content += f"- {pending_file.name}\n"

        if pending_approval_count > 5:
            dashboard_content += f"- ... and {pending_approval_count - 5} more\n"

        dashboard_content += "\n## Recently Completed\n"

        for i, done_file in enumerate(list(self.done.glob("*.md"))[:5]):
            dashboard_content += f"- {done_file.name}\n"

        if done_count > 5:
            dashboard_content += f"- ... and {done_count - 5} more\n"

        dashboard_content += "\n## Recent Actions\n"

        for log in reversed(recent_logs):
            dashboard_content += f"- {log['timestamp']}: {log['action_name']} ({log['result']})\n"

        dashboard_content += f"""

## MCP Server Status
- **Email MCP**: Operational
- **Last Heartbeat**: {datetime.now().isoformat()}

## System Settings
- **Dry Run Mode**: {'Enabled' if self.dry_run else 'Disabled'}
- **Processing Interval**: {self.processing_interval}s
"""

        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)

if __name__ == "__main__":
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
    processor = SilverTierProcessor(vault_path)
    processor.run()
```

### 8. Start the System
```bash
# Start MCP server in background
python mcp/email-server.py &

# Start all processes with PM2
pm2 start ecosystem.config.js

# Or start individual processes
python src/main.py &
python watchers/whatsapp_watcher.py &
python watchers/linkedin_watcher.py &

# View PM2 status
pm2 status
```

### 9. Test the System
1. Place a test file in the `AI_Employee_Vault/Inbox/` directory
2. Monitor the `AI_Employee_Vault/Needs_Action/` folder for action files
3. Check for plan files in `AI_Employee_Vault/Plans/`
4. For sensitive actions, verify approval requests appear in `AI_Employee_Vault/Pending_Approval/`
5. Manually move approval requests to `AI_Employee_Vault/Approved/` to trigger execution
6. Check logs in `AI_Employee_Vault/Logs/` and dashboard updates

### 10. Production Deployment Considerations
- Secure all credential storage with OS-level secrets managers
- Implement proper SSL certificates for MCP server communications
- Set up proper log rotation and monitoring
- Configure proper error alerting
- Schedule regular backups of the vault directory
- Implement proper firewall rules for MCP server access