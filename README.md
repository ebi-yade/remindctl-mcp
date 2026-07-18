# remindctl-mcp

MCP server for [Apple Reminders](https://support.apple.com/guide/reminders/welcome/mac) via [remindctl](https://github.com/openclaw/remindctl).

Lets any MCP-compatible AI assistant (Amazon Quick, Claude Desktop, etc.) read and write your Apple Reminders through the standard [Model Context Protocol](https://modelcontextprotocol.io/).

## Requirements

- macOS 14+ (Sonoma or later)
- [remindctl](https://github.com/openclaw/remindctl) installed (`brew install steipete/tap/remindctl`)
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Setup (Amazon Quick)

### 1. Clone & install dependencies

```bash
git clone https://github.com/ebi-yade/remindctl-mcp.git
cd ./remindctl-mcp
uv venv
uv pip install mcp
```

### 2. Register as MCP server

Open **Settings → Capabilities → Connectors → + Add MCP server** and configure:

| Field | Value |
|-------|-------|
| Name | `remindctl` |
| Command | `/path/to/remindctl-mcp/.venv/bin/python` |
| Args | `/path/to/remindctl-mcp/server.py` |

Replace `/path/to/` with the actual location (e.g. `/Users/you/remindctl-mcp/`).

### 3. Grant Reminders permission

macOS controls Reminders access via TCC. Permission is granted to the **host app** that spawns the MCP server process (e.g. Amazon Quick), not to `python` or `remindctl` directly.

1. Ask the assistant to call `reminders_authorize`
2. A macOS dialog will appear — click **OK**
3. Verify with `reminders_status` → should show `"authorized": true`

## TCC Troubleshooting

If any tool returns "Reminders access denied", the fix is always the same:

```bash
# 1. Reset permission to trigger a fresh prompt
tccutil reset Reminders <bundle_id>

# For Amazon Quick:
tccutil reset Reminders com.amazon.QuickWork.mac
```

Then ask the assistant to call `reminders_authorize` again and click **OK** on the dialog.

> **Why this happens:** macOS may revoke TCC grants after OS updates, or the user may have accidentally denied the prompt. `tccutil reset` clears the decision so the dialog can appear again.

## Tools

| Tool | Description |
|------|-------------|
| `reminders_authorize` | Trigger TCC permission dialog (for initial setup / recovery) |
| `reminders_status` | Check authorization status |
| `reminders_show` | Show reminders by filter (today, week, overdue, etc.) |
| `reminders_search` | Search reminders by keyword |
| `reminders_lists` | List all reminder lists or show reminders in specific list(s) |
| `reminders_add` | Create a new reminder |
| `reminders_edit` | Edit an existing reminder |
| `reminders_complete` | Mark reminders as complete |
| `reminders_delete` | Delete reminders |

## How it works

```
MCP Host (Amazon Quick, Claude, etc.)
  ↕ stdio (JSON-RPC)
remindctl-mcp (this server)
  ↕ subprocess
remindctl CLI
  ↕ EventKit API
Apple Reminders (syncs via iCloud)
```

The server is a thin wrapper: it translates MCP tool calls into `remindctl` CLI invocations and returns JSON output. No data is stored or cached — all state lives in Apple Reminders.

## Other MCP hosts

This server uses stdio transport and works with any MCP client. For Claude Desktop, add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "remindctl": {
      "command": "/path/to/remindctl-mcp/.venv/bin/python",
      "args": ["/path/to/remindctl-mcp/server.py"]
    }
  }
}
```

## License

MIT
