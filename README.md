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
git clone https://github.com/ebi-yade/remindctl-mcp.git ~/remindctl-mcp
cd ~/remindctl-mcp
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

### 3. Grant Reminders permission (TCC)

On first use, macOS needs to grant the MCP host app access to Reminders.

1. Make sure Amazon Quick's window is **in the foreground**
2. Ask the assistant to call `reminders_authorize`
3. A macOS dialog will appear — click **OK** to allow access
4. Verify with `reminders_status` → should show `"authorized": true`

## TCC Troubleshooting

macOS controls Reminders access via TCC (Transparency, Consent, and Control). Permission is tied to the **host app** that spawns the MCP server process — not to `python` or `remindctl` directly.

### "Access denied" after it was working

The TCC permission may have been reset (macOS updates, manual reset, etc.).

**Recovery:**

1. Ask the assistant to call `reminders_authorize` — this triggers the macOS permission dialog via `osascript`
2. If a dialog appears, click **OK**
3. If no dialog appears and status still shows denied:

```bash
# Reset TCC for the host app to force a fresh prompt
tccutil reset Reminders <bundle_id>
# e.g. for Amazon Quick:
tccutil reset Reminders com.amazon.QuickWork.mac
```

Then retry `reminders_authorize`.

### "Access denied" but no dialog appears

This typically happens when:
- The host app is **in the background** — bring it to the foreground and retry
- TCC state is `denied` (not `not-determined`) — you must reset first with `tccutil reset` (see above), then retry

### Permission was accidentally denied

If you clicked "Don't Allow" on the TCC dialog:

1. Reset with `tccutil reset Reminders <bundle_id>`
2. Call `reminders_authorize` again
3. This time click **OK**

Or manually: **System Settings → Privacy & Security → Reminders** → find the host app and toggle it on.

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
