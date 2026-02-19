# Retry Failed Action

Automatically retry failed MCP operations with exponential backoff and permanent failure alerting.

## Description
This skill manages a persistent retry queue for MCP operations that fail due to transient errors (network timeouts, rate limits, temporary server issues). Failed operations are queued with exponential backoff (30s → 60s → 120s) and retried up to 3 times. If all retries exhaust, a permanent failure alert is created in `/Needs_Action/` for human attention. The queue is persisted as Markdown in the vault.

## When to Use
- An MCP server call fails during action execution
- The retry queue has entries that are due for retry (checked every processing cycle)
- A permanent failure needs human notification

## Inputs
- Failed MCP operation details: server name, method, parameters, error message
- Retry queue file: `AI_Employee_Vault/Business/retry_queue.md`
- Processing cycle triggers from Gold processor

## Outputs
- Retry queue entries in `AI_Employee_Vault/Business/retry_queue.md`
- Successful retries: entry removed from queue, action completed
- Permanent failures: alert file in `AI_Employee_Vault/Needs_Action/ALERT_retry_failed_[id].md`

## Approval Required
- **No** — retries are automatic for already-approved actions

## MCP Servers Used
- Any server that was originally called: `email_mcp`, `linkedin_mcp`, `twitter_mcp`, `facebook_mcp`, `instagram_mcp`, `whatsapp_mcp`, `odoo_mcp`

## Exponential Backoff Schedule
| Attempt | Delay | Total Wait |
|---------|-------|------------|
| 1st retry | 30 seconds | 30s |
| 2nd retry | 60 seconds | 1.5 min |
| 3rd retry | 120 seconds | 3.5 min |
| Exhausted | — | Permanent failure alert |

Formula: `delay = 30 * (2 ^ retry_count)` seconds

## Retry Queue Entry Format
Persisted as Markdown in `Business/retry_queue.md`:
```markdown
## Retry: retry_1708300000_email_send

- **Operation**: send_email
- **MCP Server**: email_mcp
- **Parameters**: {"to": ["user@example.com"], "subject": "Invoice"}
- **Approval Ref**: approval_1708299900.md
- **Retry Count**: 1/3
- **Last Attempt**: 2026-02-19T09:00:00
- **Next Retry After**: 2026-02-19T09:01:00
- **Error**: Server timed out
- **Status**: queued

---
```

## Entry Statuses
| Status | Meaning |
|--------|---------|
| `queued` | Waiting for next retry window |
| `retrying` | Currently being retried |
| `failed_permanent` | All retries exhausted |

## Permanent Failure Alert
When max retries are exhausted, an urgent alert is created:
```markdown
---
priority: urgent
domain: business
---
# ALERT: Permanent Failure

**Operation**: send_email
**MCP Server**: email_mcp
**Error**: Server timed out
**Retries Exhausted**: 3/3

This operation has failed permanently after 3 retries.
Please investigate and retry manually.
```

## Process Steps

### Adding to Queue
1. MCP call fails during `_execute_via_mcp()`
2. `RetryQueueEntry` created with operation details
3. `calculate_next_retry()` sets backoff delay
4. Entry added to queue via `RetryManager.add_to_queue()`
5. Queue saved to `Business/retry_queue.md`

### Processing Queue (every cycle)
1. `GoldProcessor._process_retry_queue()` called during `process_all()`
2. `RetryManager.get_ready_entries()` finds entries past their `next_retry_after`
3. For each ready entry:
   a. Set status to `retrying`
   b. Call MCP server with original parameters
   c. On success: remove entry from queue
   d. On failure: increment retry count, calculate new backoff
   e. If max retries reached: create permanent failure alert

### Queue Persistence
- Queue is stored as Markdown (readable in Obsidian)
- Loaded on processor startup via `RetryManager.load_queue()`
- Saved after every modification
- Survives process restarts

## Code Reference
- `src/utils/retry_manager.py` — RetryManager (add_to_queue, get_ready_entries, update_entry, remove_entry)
- `src/models/retry_queue_entry.py` — RetryQueueEntry (data model, Markdown serialization, backoff calculation)
- `src/processors/gold_processor.py` — `_process_retry_queue()`, `_notify_permanent_failure()`

## Quality Criteria
- Backoff delays are correctly calculated (30s, 60s, 120s)
- Queue survives process restarts (Markdown persistence)
- Successful retries remove entries (no stale queue buildup)
- Permanent failures always generate urgent alerts
- Original operation parameters are preserved exactly across retries
- Queue depth is trackable via `RetryManager.queue_depth`

## Related Skills
- `auto-approve-action` — Failed auto-approved executions enter the retry queue
- `send-email-mcp` — Email failures are retried through this skill
- `social-media-post` — Social media failures are retried through this skill
- `audit-log` — Retry attempts and permanent failures are logged
