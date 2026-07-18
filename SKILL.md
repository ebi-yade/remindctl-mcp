---
name: remindctl-mcp
display_name: "Apple Reminders (remindctl)"
description: "Use when the user mentions Apple Reminders, リマインダー, reminder lists, buying lists (買い物リスト), recurring tasks, or asks to add/check/complete reminders on their Apple devices."
icon: "🔔"
trigger: reminders リマインダー reminder 買い物リスト routine overdue
integration: remindctl
---

## Overview

Manage Apple Reminders on macOS via the `remindctl` MCP server. Changes sync through iCloud to all Apple devices. Supports showing, searching, creating, editing, completing, and deleting reminders — including recurring ones with due dates, alarms, and location triggers.

## Tools

- `reminders_authorize` — Trigger TCC permission dialog (osascript). Use when any tool returns "access denied."
- `reminders_status` — Check authorization. Returns `{ authorized, status }`.
- `reminders_show` — Show reminders by filter + optional list.
- `reminders_search` — Search titles, notes, and URLs.
- `reminders_lists` — List all lists (no args), or show reminders in specific list(s) (comma-separated names).
- `reminders_add` — Create a reminder.
- `reminders_edit` — Edit by index or ID prefix.
- `reminders_complete` — Mark complete (comma-separated IDs).
- `reminders_delete` — Delete (comma-separated IDs, forced).
- `remindctl_raw` — **Fallback.** Run any `remindctl` command directly. For operations not covered by the tools above.

## Workflow

### Step 1: Check Authorization (if first use or error)
- **Mode**: `deterministic`
- **Tool**: `reminders_status`
- **Input**: none
- **Output**: `{ authorized: bool, status: string }`
- **Validate**: `authorized` is `true`
- **On failure**: Call `reminders_authorize`. If that times out (~10s), a TCC dialog appeared — tell the user to click OK, then retry. If status is `denied` (not `not-determined`), tell the user to run `tccutil reset Reminders com.amazon.QuickWork.mac` first, then call `reminders_authorize` again.

### Step 2: Fulfill the Request
- **Mode**: `agentic`
- **Input**: User's intent (show, add, edit, complete, search, etc.)
- **Output**: Reminder data or confirmation of mutation
- **Tool selection**: Use the dedicated tool if one exists for the operation. Fall back to `remindctl_raw` for anything else (list management, export, etc.).

## Tool Usage Notes

### reminders_show vs reminders_lists

| | `reminders_show` | `reminders_lists` |
|--|--|--|
| Without list arg | All reminders matching the filter | All lists with metadata (counts) |
| With list name(s) | Reminders matching filter in that list | All reminders in that list (including completed) |
| Use when | "What's due today?" "Show overdue" | "What lists do I have?" "Show everything in a list" |

Filters for `reminders_show`: `today`, `tomorrow`, `week`, `overdue`, `upcoming`, `open`, `completed`, `all`, or `YYYY-MM-DD`.

### remindctl_raw (fallback)

Pass the command string as you would on CLI, without the `remindctl` prefix. `--json` and `--no-input` are appended automatically.

Use for operations that don't have a dedicated tool:
- **Create a list**: `list Shopping --create`
- **Rename a list**: `list OldName --rename NewName`
- **Delete a list**: `list OldList --delete --force`
- **Export**: `export --list Work --export-format csv`
- **Info on a single reminder**: `info 4A83`
- **Open in Reminders.app**: `open 1`

Do NOT use `remindctl_raw` for operations that already have a dedicated tool (show, search, add, edit, complete, delete) — the dedicated tools have better argument validation.

### Recurring reminders

Both `show` and `lists` return a `recurrenceRule` field when set:
```json
{ "frequency": "daily", "interval": 1 }
```
Supported: `daily`, `weekly`, `biweekly`, `monthly`, `yearly`, `every N days/weeks/months/years`.

When a recurring reminder is `complete`d, the system automatically advances the due date to the next occurrence. Overdue recurring items don't need to be deleted — just completed to advance.

### reminders_add

- `title` is required; everything else is optional.
- `due` accepts: `today`, `tomorrow`, `YYYY-MM-DD`, `YYYY-MM-DD HH:mm`
- Date-only = all-day reminder. Date-time = timed (auto-alarm at due time).
- `reminder_list` — target list name. If omitted, uses system default.
- Confirm title, list, and due before creating if any are ambiguous.

### reminders_edit

- Pass only the fields to change. Use `clear_due`, `clear_alarm`, `clear_url`, `no_repeat` booleans to remove values.
- Move between lists: pass `reminder_list` with the new list name (no need to delete + recreate).

### reminders_complete / reminders_delete

- Accept comma-separated indexes or ID prefixes (from `show`/`lists` output).
- `delete` is forced (no confirmation prompt) — confirm with user before calling.
- `complete` on a recurring reminder advances the due date; `delete` permanently removes it.

### Authorization errors

If any tool returns "Reminders access denied":
1. Call `reminders_authorize`
2. If it times out → TCC dialog appeared → tell user to click OK → retry
3. If status is `denied` → user must `tccutil reset Reminders com.amazon.QuickWork.mac` → then `reminders_authorize`

## Limitations

remindctl uses public EventKit APIs. Not available:
- Native Reminders sections, tags, smart lists
- File/image attachments
- Apple's private "Urgent" toggle
