#!/usr/bin/env python3
"""
Slack Enterprise MCP Server
============================
Enterprise-grade Slack integration with full audit trails for compliance.
Every action is logged locally for governance and regulatory requirements.

Built by MEOK AI Labs.

Install: pip install mcp slack_sdk
Run:     SLACK_BOT_TOKEN=xoxb-... python server.py
"""


import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
AUDIT_LOG_PATH = Path(os.environ.get("AUDIT_LOG_PATH", "audit_log.jsonl"))

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------
FREE_DAILY_LIMIT = 100
PRO_DAILY_LIMIT = 10_000
_usage: dict[str, list[datetime]] = defaultdict(list)


def _check_rate_limit(caller: str = "anonymous", tier: str = "free") -> Optional[str]:
    """Returns error string if rate-limited, else None."""
    limit = PRO_DAILY_LIMIT if tier == "pro" else FREE_DAILY_LIMIT
    now = datetime.now()
    cutoff = now - timedelta(days=1)
    _usage[caller] = [t for t in _usage[caller] if t > cutoff]
    if len(_usage[caller]) >= limit:
        return f"Rate limit reached ({limit}/day). Upgrade to Pro for higher limits: https://meok.ai/mcp/slack-enterprise/pro"
    _usage[caller].append(now)
    return None


# ---------------------------------------------------------------------------
# Audit logging — enterprise differentiator
# ---------------------------------------------------------------------------
_audit_entries: list[dict] = []


def _audit_log(action: str, params: dict, result_summary: str, caller: str = "anonymous") -> None:
    """Log every MCP action to local audit file and in-memory buffer."""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "caller": caller,
        "params": {k: v for k, v in params.items() if k not in ("token")},
        "result_summary": result_summary[:500],
    }
    _audit_entries.append(entry)
    try:
        with open(AUDIT_LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass  # non-blocking — audit file write failure shouldn't break operations


# ---------------------------------------------------------------------------
# Slack client helper
# ---------------------------------------------------------------------------
def _get_client():
    """Return a Slack WebClient, raising if no token configured."""
    if not SLACK_BOT_TOKEN:
        raise ValueError(
            "SLACK_BOT_TOKEN environment variable is required. "
            "Create a Slack app at https://api.slack.com/apps and add a Bot Token."
        )
    from slack_sdk import WebClient
    return WebClient(token=SLACK_BOT_TOKEN)


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "Slack Enterprise MCP",
    instructions=(
        "Enterprise Slack integration with compliance audit trails. "
        "Every action is logged for governance. Requires SLACK_BOT_TOKEN env var."
    ))


@mcp.tool()
def send_message(channel: str, text: str, thread_ts: str = "", api_key: str = "") -> dict:
    """Send a message to a Slack channel or thread. Every message is audit-logged
    for enterprise compliance. Provide channel name (e.g. #general) or channel ID.
    Optionally provide thread_ts to reply in a thread."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/14A4gB3K4eUWgYR56o8k836"}

    err = _check_rate_limit()
    if err:
        return {"error": err}

    try:
        client = _get_client()
        kwargs = {"channel": channel, "text": text}
        if thread_ts:
            kwargs["thread_ts"] = thread_ts

        response = client.chat_postMessage(**kwargs)
        result = {
            "ok": response["ok"],
            "channel": response["channel"],
            "ts": response["ts"],
            "message": response.get("message", {}).get("text", ""),
        }
        _audit_log("send_message", {"channel": channel, "text_length": len(text), "thread_ts": thread_ts},
                    f"Sent to {channel}, ts={response['ts']}")
        return result
    except Exception as e:
        _audit_log("send_message", {"channel": channel}, f"ERROR: {str(e)}")
        return {"error": str(e)}


@mcp.tool()
def search_messages(query: str, count: int = 20, sort: str = "timestamp", api_key: str = "") -> dict:
    """Search messages across the entire Slack workspace. Supports Slack search
    modifiers like 'in:#channel', 'from:@user', 'before:2024-01-01'.
    Sort by 'timestamp' (newest first) or 'score' (most relevant)."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/14A4gB3K4eUWgYR56o8k836"}

    err = _check_rate_limit()
    if err:
        return {"error": err}

    try:
        client = _get_client()
        response = client.search_messages(query=query, count=min(count, 100), sort=sort)
        messages = []
        for match in response.get("messages", {}).get("matches", []):
            messages.append({
                "text": match.get("text", "")[:500],
                "user": match.get("user", ""),
                "username": match.get("username", ""),
                "channel": match.get("channel", {}).get("name", ""),
                "ts": match.get("ts", ""),
                "permalink": match.get("permalink", ""),
            })
        result = {
            "total": response.get("messages", {}).get("total", 0),
            "messages": messages,
        }
        _audit_log("search_messages", {"query": query, "count": count}, f"Found {result['total']} results")
        return result
    except Exception as e:
        _audit_log("search_messages", {"query": query}, f"ERROR: {str(e)}")
        return {"error": str(e)}


@mcp.tool()
def list_channels(limit: int = 100, types: str = "public_channel", api_key: str = "") -> dict:
    """List Slack channels with member counts and topics. Types can be
    'public_channel', 'private_channel', or 'public_channel,private_channel'."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/14A4gB3K4eUWgYR56o8k836"}

    err = _check_rate_limit()
    if err:
        return {"error": err}

    try:
        client = _get_client()
        response = client.conversations_list(limit=min(limit, 1000), types=types)
        channels = []
        for ch in response.get("channels", []):
            channels.append({
                "id": ch["id"],
                "name": ch.get("name", ""),
                "topic": ch.get("topic", {}).get("value", ""),
                "purpose": ch.get("purpose", {}).get("value", ""),
                "num_members": ch.get("num_members", 0),
                "is_archived": ch.get("is_archived", False),
                "created": ch.get("created", 0),
            })
        channels.sort(key=lambda c: c["num_members"], reverse=True)
        result = {"channels": channels, "count": len(channels)}
        _audit_log("list_channels", {"types": types}, f"Listed {len(channels)} channels")
        return result
    except Exception as e:
        _audit_log("list_channels", {}, f"ERROR: {str(e)}")
        return {"error": str(e)}


@mcp.tool()
def get_thread(channel: str, thread_ts: str, limit: int = 50, api_key: str = "") -> dict:
    """Get a full thread with all replies. Provide the channel ID and the
    thread's parent message timestamp (thread_ts)."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/14A4gB3K4eUWgYR56o8k836"}

    err = _check_rate_limit()
    if err:
        return {"error": err}

    try:
        client = _get_client()
        response = client.conversations_replies(channel=channel, ts=thread_ts, limit=min(limit, 200))
        messages = []
        for msg in response.get("messages", []):
            messages.append({
                "user": msg.get("user", ""),
                "text": msg.get("text", "")[:1000],
                "ts": msg.get("ts", ""),
                "reply_count": msg.get("reply_count", 0),
            })
        result = {"messages": messages, "count": len(messages), "thread_ts": thread_ts}
        _audit_log("get_thread", {"channel": channel, "thread_ts": thread_ts}, f"Retrieved {len(messages)} messages")
        return result
    except Exception as e:
        _audit_log("get_thread", {"channel": channel, "thread_ts": thread_ts}, f"ERROR: {str(e)}")
        return {"error": str(e)}


@mcp.tool()
def create_channel(name: str, description: str = "", is_private: bool = False, api_key: str = "") -> dict:
    """Create a new Slack channel. Name must be lowercase, no spaces (use hyphens).
    Optionally set a description/purpose and make it private."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/14A4gB3K4eUWgYR56o8k836"}

    err = _check_rate_limit()
    if err:
        return {"error": err}

    try:
        client = _get_client()
        response = client.conversations_create(name=name, is_private=is_private)
        channel_id = response["channel"]["id"]

        if description:
            client.conversations_setPurpose(channel=channel_id, purpose=description)

        result = {
            "ok": True,
            "channel_id": channel_id,
            "name": response["channel"]["name"],
            "is_private": is_private,
        }
        _audit_log("create_channel", {"name": name, "is_private": is_private},
                    f"Created channel {name} ({channel_id})")
        return result
    except Exception as e:
        _audit_log("create_channel", {"name": name}, f"ERROR: {str(e)}")
        return {"error": str(e)}


@mcp.tool()
def set_channel_topic(channel: str, topic: str, api_key: str = "") -> dict:
    """Update the topic of a Slack channel. Provide channel ID or name."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/14A4gB3K4eUWgYR56o8k836"}

    err = _check_rate_limit()
    if err:
        return {"error": err}

    try:
        client = _get_client()
        response = client.conversations_setTopic(channel=channel, topic=topic)
        result = {
            "ok": True,
            "channel": channel,
            "topic": response.get("channel", {}).get("topic", {}).get("value", topic),
        }
        _audit_log("set_channel_topic", {"channel": channel, "topic": topic[:100]},
                    f"Updated topic for {channel}")
        return result
    except Exception as e:
        _audit_log("set_channel_topic", {"channel": channel}, f"ERROR: {str(e)}")
        return {"error": str(e)}


@mcp.tool()
def get_audit_log(limit: int = 50, action_filter: str = "", api_key: str = "") -> dict:
    """Return the audit trail of all MCP actions performed through this server.
    Enterprise compliance feature -- shows who did what and when.
    Optionally filter by action name (e.g. 'send_message', 'create_channel')."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/14A4gB3K4eUWgYR56o8k836"}

    err = _check_rate_limit()
    if err:
        return {"error": err}

    entries = _audit_entries
    if action_filter:
        entries = [e for e in entries if e["action"] == action_filter]

    # Return most recent entries
    recent = entries[-limit:]
    recent.reverse()  # newest first

    result = {
        "entries": recent,
        "total_logged": len(_audit_entries),
        "filtered_count": len(entries),
        "returned_count": len(recent),
        "audit_file": str(AUDIT_LOG_PATH),
    }
    _audit_log("get_audit_log", {"limit": limit, "action_filter": action_filter},
                f"Retrieved {len(recent)} audit entries")
    return result


@mcp.tool()
def summarize_channel(channel: str, message_count: int = 50, api_key: str = "") -> dict:
    """Get the last N messages from a channel and provide a structured summary.
    Returns messages grouped by topic threads, active participants, and key highlights."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://buy.stripe.com/14A4gB3K4eUWgYR56o8k836"}

    err = _check_rate_limit()
    if err:
        return {"error": err}

    try:
        client = _get_client()
        response = client.conversations_history(channel=channel, limit=min(message_count, 200))
        messages = response.get("messages", [])

        # Build summary data
        participants: dict[str, int] = defaultdict(int)
        thread_count = 0
        total_reactions = 0
        texts = []

        for msg in messages:
            user = msg.get("user", "unknown")
            participants[user] += 1
            if msg.get("reply_count", 0) > 0:
                thread_count += 1
            total_reactions += len(msg.get("reactions", []))
            texts.append({
                "user": user,
                "text": msg.get("text", "")[:300],
                "ts": msg.get("ts", ""),
                "reply_count": msg.get("reply_count", 0),
                "reactions": len(msg.get("reactions", [])),
            })

        # Sort participants by activity
        top_participants = sorted(participants.items(), key=lambda x: x[1], reverse=True)[:10]

        result = {
            "channel": channel,
            "message_count": len(messages),
            "active_threads": thread_count,
            "total_reactions": total_reactions,
            "top_participants": [{"user": u, "message_count": c} for u, c in top_participants],
            "unique_participants": len(participants),
            "messages": texts,
            "time_range": {
                "oldest": messages[-1]["ts"] if messages else None,
                "newest": messages[0]["ts"] if messages else None,
            },
        }
        _audit_log("summarize_channel", {"channel": channel, "message_count": message_count},
                    f"Summarized {len(messages)} messages from {channel}")
        return result
    except Exception as e:
        _audit_log("summarize_channel", {"channel": channel}, f"ERROR: {str(e)}")
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()
