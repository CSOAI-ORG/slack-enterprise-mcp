# Slack Enterprise MCP Server

> **By [MEOK AI Labs](https://meok.ai)** — Sovereign AI tools for everyone.

Enterprise-grade Slack integration with compliance audit trails for AI agents. Every action is logged locally for governance, regulatory compliance, and security review.

[![MCPize](https://img.shields.io/badge/MCPize-Listed-blue)](https://mcpize.com/mcp/slack-enterprise)
[![MIT License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-255+_servers-purple)](https://meok.ai)

## Tools

| Tool | Description |
|------|-------------|
| `send_message` | Send a message to a Slack channel or thread |
| `search_messages` | Search messages across the workspace |
| `list_channels` | List Slack channels with member counts and topics |
| `get_thread` | Get a full thread with all replies |
| `create_channel` | Create a new Slack channel |
| `set_channel_topic` | Update the topic of a Slack channel |
| `get_audit_log` | Return the audit trail of all MCP actions |
| `summarize_channel` | Get and summarize the last N messages from a channel |

## Quick Start

```bash
pip install mcp
git clone https://github.com/CSOAI-ORG/slack-enterprise-mcp.git
cd slack-enterprise-mcp
python server.py
```

## Claude Desktop Config

```json
{
  "mcpServers": {
    "slack-enterprise": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/slack-enterprise-mcp"
    }
  }
}
```

## Pricing

| Plan | Price | Requests |
|------|-------|----------|
| Free | $0/mo | 100 calls/day |
| Pro | $12/mo | 10,000 calls/day + priority |
| Enterprise | Contact us | Custom + SLA + on-prem audit |

[Get on MCPize](https://mcpize.com/mcp/slack-enterprise)

## Part of MEOK AI Labs

This is one of 255+ MCP servers by MEOK AI Labs. Browse all at [meok.ai](https://meok.ai) or [GitHub](https://github.com/CSOAI-ORG).

---
**MEOK AI Labs** | [meok.ai](https://meok.ai) | nicholas@meok.ai | United Kingdom
