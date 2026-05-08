[![slack-enterprise-mcp MCP server](https://glama.ai/mcp/servers/CSOAI-ORG/slack-enterprise-mcp/badges/score.svg)](https://glama.ai/mcp/servers/CSOAI-ORG/slack-enterprise-mcp)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-Published-green)](https://registry.modelcontextprotocol.io)
[![PyPI](https://img.shields.io/pypi/v/slack-enterprise-mcp)](https://pypi.org/project/slack-enterprise-mcp/)

[![slack-enterprise-mcp MCP server](https://glama.ai/mcp/servers/CSOAI-ORG/slack-enterprise-mcp/badges/card.svg)](https://glama.ai/mcp/servers/CSOAI-ORG/slack-enterprise-mcp)

<div align="center">

# Slack Enterprise MCP

**MCP server for slack enterprise mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-slack-enterprise-mcp)](https://pypi.org/project/meok-slack-enterprise-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Slack Enterprise MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `send_message` | Send a message to a Slack channel or thread. Every message is audit-logged |
| `search_messages` | Search messages across the entire Slack workspace. Supports Slack search |
| `list_channels` | List Slack channels with member counts and topics. Types can be |
| `get_thread` | Get a full thread with all replies. Provide the channel ID and the |
| `create_channel` | Create a new Slack channel. Name must be lowercase, no spaces (use hyphens). |
| `set_channel_topic` | Update the topic of a Slack channel. Provide channel ID or name. |
| `get_audit_log` | Return the audit trail of all MCP actions performed through this server. |
| `summarize_channel` | Get the last N messages from a channel and provide a structured summary. |

## Installation

```bash
pip install meok-slack-enterprise-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config:

```json
{
  "mcpServers": {
    "slack-enterprise-mcp": {
      "command": "python",
      "args": ["-m", "meok_slack_enterprise_mcp.server"]
    }
  }
}
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
<!-- mcp-name: io.github.CSOAI-ORG/slack-enterprise-mcp -->
