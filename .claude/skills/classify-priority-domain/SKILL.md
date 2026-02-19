# Classify Priority & Domain

Determine action item priority (urgent/high/normal/low) and domain (personal/business/cross-domain) for intelligent processing order.

## Description
This skill classifies every incoming action item on two axes: **priority** (how urgent it is) and **domain** (personal vs business context). Classification drives Gold tier's smart processing — urgent items are handled first, cross-domain items get extra scrutiny, and domain tags feed into business reports. Classification uses frontmatter metadata first, then falls back to keyword inference from content.

## When to Use
- When a new file appears in `/Needs_Action/`
- Before deciding processing order in the Gold processor queue
- Before routing to auto-approval (cross-domain items are never auto-approved)
- When generating audit reports that break down activity by domain

## Inputs
- Markdown action file content (full text)
- YAML frontmatter (if present) with optional `priority:` and `domain:` fields

## Outputs
- `priority: str` — one of `urgent`, `high`, `normal`, `low`
- `domain: str` — one of `personal`, `business`, `cross-domain`

## Approval Required
- **No** — classification is internal analysis, no external action

## MCP Servers Used
- None

## Priority Classification

### Precedence Order
1. Frontmatter `priority:` field (if valid value)
2. Keyword inference from content
3. Default: `normal`

### Priority Keywords
| Priority | Keywords |
|----------|----------|
| **Urgent** | urgent, deadline, asap, critical, immediately, emergency |
| **High** | important, financial, high priority, time-sensitive, revenue |
| **Low** | low-priority, optional, when possible, nice to have, backlog |
| **Normal** | Everything else (default) |

### Processing Order
```
urgent (0) → high (1) → normal (2) → low (3)
```
Gold processor sorts the queue by this order before processing.

## Domain Classification

### Precedence Order
1. Frontmatter `domain:` field (if valid value)
2. Keyword inference from content
3. Default: `personal`

### Domain Keywords
| Domain | Keywords |
|--------|----------|
| **Business** | invoice, expense, revenue, client, vendor, tax, accounting, bookkeeping, profit, budget, quarterly, financial, payroll, contract, supplier, procurement |
| **Personal** | personal, home, family, calendar, reminder, grocery, appointment, birthday, vacation, hobby, health, fitness, recipe, private |
| **Cross-domain** | Both business AND personal keywords detected |

### Cross-Domain Impact
- Cross-domain items are **never auto-approved** (require human review)
- They are flagged in audit reports for visibility

## Frontmatter Examples

### Explicit priority and domain
```yaml
---
priority: urgent
domain: business
---
# Invoice overdue for Client XYZ
```

### Keyword-inferred (no frontmatter)
```markdown
# Reminder: Buy groceries for family dinner
Pick up items for Saturday's birthday party.
```
Result: `priority=normal`, `domain=personal` (matches "family", "grocery", "birthday")

### Cross-domain detection
```markdown
# Schedule vendor meeting and personal dentist appointment
Need to meet the supplier at 2pm and dentist at 4pm.
```
Result: `priority=normal`, `domain=cross-domain` (matches "vendor"+"supplier" AND "personal"+"appointment")

## Process Steps
1. Parse YAML frontmatter from Markdown content via `parse_frontmatter()`
2. Check frontmatter for explicit `priority:` — use if valid
3. If no valid frontmatter priority, scan content for priority keywords
4. Check frontmatter for explicit `domain:` — use if valid
5. If no valid frontmatter domain, scan for business and personal keywords
6. If both business and personal keywords found → `cross-domain`
7. Return `(priority, domain)` tuple to Gold processor

## Code Reference
- `src/utils/priority_classifier.py` — `classify_priority()`, `parse_frontmatter()`
- `src/utils/domain_classifier.py` — `classify_domain()`
- `src/processors/gold_processor.py` — `_process_needs_action_gold()` (uses both classifiers)

## Quality Criteria
- Frontmatter values always take precedence over keyword inference
- Invalid frontmatter values are ignored (fall through to keywords)
- Cross-domain is only assigned when BOTH business and personal keywords are present
- Default priority is `normal`, default domain is `personal`
- Classification is deterministic and testable (no randomness)

## Test Coverage
```python
assert classify_priority("URGENT: server is down") == "urgent"
assert classify_priority("Update the report") == "normal"
assert classify_priority("", {"priority": "high"}) == "high"
assert classify_priority("", {"priority": "invalid"}) == "normal"

assert classify_domain("Send invoice to client") == "business"
assert classify_domain("Buy groceries for family") == "personal"
assert classify_domain("Meet vendor and pick up kids") == "cross-domain"
assert classify_domain("", {"domain": "business"}) == "business"
```

## Related Skills
- `process-needs-action` — Triggers classification during processing
- `auto-approve-action` — Uses domain to block cross-domain auto-approval
- `generate-business-report` — Reports break down activity by domain
