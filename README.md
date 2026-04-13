# Slack Enterprise MCP Server

Enterprise-grade Slack integration with compliance audit trails for AI agents. Every action is logged locally for governance, regulatory compliance, and security review.

Built by [MEOK AI Labs](https://meok.ai) -- the team behind MEOK AI OS (22 APIs, 15 AI models, 307 tests).

## Why this exists

Existing Slack MCP servers send messages and search -- but none provide the audit trail that enterprise teams require. This server logs every action with timestamps, caller identity, and operation details to a local JSONL file and in-memory buffer, enabling compliance review without external dependencies.

## Tools

| Tool | Description |
|------|-------------|
| `send_message` | Send message to channel or thread (audit-logged) |
| `search_messages` | Search across workspace with Slack modifiers |
| `list_channels` | List channels with member counts and topics |
| `get_thread` | Get full thread with all replies |
| `create_channel` | Create new channel with description |
| `set_channel_topic` | Update channel topic |
| `get_audit_log` | Retrieve audit trail of all MCP actions (enterprise feature) |
| `summarize_channel` | Get last N messages with participant and activity breakdown |

## Installation

```bash
pip install mcp slack_sdk
```

## Configuration

Set the `SLACK_BOT_TOKEN` environment variable. Create a Slack app at https://api.slack.com/apps with the following Bot Token Scopes:

- `chat:write` -- send messages
- `channels:read` -- list channels
- `channels:history` -- read channel history
- `groups:read` -- list private channels
- `groups:history` -- read private channel history
- `search:read` -- search messages

Optional environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SLACK_BOT_TOKEN` | (required) | Slack Bot User OAuth Token |
| `AUDIT_LOG_PATH` | `audit_log.jsonl` | Path for the audit log file |

## Usage

### Run the server

```bash
SLACK_BOT_TOKEN=xoxb-your-token python server.py
```

### Claude Desktop config

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "slack-enterprise": {
      "command": "python",
      "args": ["/path/to/slack-enterprise-mcp/server.py"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-token"
      }
    }
  }
}
```

### Example calls

**Send a message:**
```
Tool: send_message
Input: {"channel": "#general", "text": "Deployment complete for v2.3.1"}
Output: {"ok": true, "channel": "C01ABC123", "ts": "1234567890.123456"}
```

**Search workspace:**
```
Tool: search_messages
Input: {"query": "deployment error in:#engineering from:@alice", "count": 10}
Output: {"total": 3, "messages": [...]}
```

**Get audit trail:**
```
Tool: get_audit_log
Input: {"limit": 20, "action_filter": "send_message"}
Output: {"entries": [{"timestamp": "2026-04-13T...", "action": "send_message", ...}], "total_logged": 142}
```

## Audit Log Format

Each line in the JSONL audit file contains:

```json
{
  "timestamp": "2026-04-13T10:30:00.000Z",
  "action": "send_message",
  "caller": "anonymous",
  "params": {"channel": "#general", "text_length": 42},
  "result_summary": "Sent to #general, ts=1234567890.123456"
}
```

Sensitive data (tokens, full message bodies) is excluded from audit logs by design.

## Security Considerations

- **Token storage**: Never commit `SLACK_BOT_TOKEN` to version control. Use environment variables or a secrets manager.
- **Audit log access**: The audit log file contains metadata about all operations. Restrict file system access to authorized users.
- **Rate limiting**: Built-in rate limiting prevents abuse. Free tier allows 100 calls/day; Pro tier allows 10,000 calls/day.
- **Data minimization**: Message text is truncated in audit logs. Full content is not persisted in the audit trail.
- **Principle of least privilege**: Request only the Slack scopes your use case requires.

## Pricing

| Tier | Limit | Price |
|------|-------|-------|
| Free | 100 calls/day | $0 |
| Pro | 10,000 calls/day + priority | $12/mo |
| Enterprise | Custom + SLA + on-prem audit | Contact us |

## License

MIT
