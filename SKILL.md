# remindctl-mcp

Use remindctl-mcp to manage Apple Reminders on macOS 14+ via the remindctl CLI.
Changes sync through the normal Reminders/iCloud path.

## Tools

### reminders_authorize

Trigger macOS TCC permission dialog. Call this when:
- `reminders_status` returns `not-determined` or `denied`
- Any other tool returns "Reminders access denied"

After calling, a macOS dialog may appear — the user must click OK.
If TCC state is `denied` (not `not-determined`), the user must first
run `tccutil reset Reminders <bundle_id>` in their terminal, then call
this tool again.

### reminders_status

Check authorization. Returns JSON with `authorized` (bool) and `status` string.
Call this before mutating data if unsure about permission state.

### reminders_show

Show reminders by filter. Filters: `today`, `tomorrow`, `week`, `overdue`,
`upcoming`, `open`, `completed`, `all`, or a date string (`YYYY-MM-DD`).
Use `reminder_list` param to limit to one list.

### reminders_search

Search reminder titles, notes, and URLs. Use `reminder_list` to scope.

### reminders_lists

No arguments: show all lists with counts.
With `names` (comma-separated): show reminders in those lists.

### reminders_add

Create a reminder. Required: `title`. Optional: `reminder_list`, `due`,
`alarm`, `notes`, `url`, `repeat`, `priority` (none/low/medium/high).

Date formats: `today`, `tomorrow`, `YYYY-MM-DD`, `YYYY-MM-DD HH:mm`.
Date-only = all-day reminder. Date-time = timed reminder with auto-alarm.

### reminders_edit

Edit by index or ID prefix. Pass only the fields you want to change.
Use `clear_due`, `clear_alarm`, `clear_url`, `no_repeat` booleans to remove values.
Move between lists with `reminder_list`.

### reminders_complete

Mark complete. Pass comma-separated indexes or ID prefixes.

### reminders_delete

Delete permanently. Pass comma-separated indexes or ID prefixes.
Deletion is forced (no confirmation prompt).

## Permission Recovery Flow

1. Call `reminders_status`
2. If `not-determined`: call `reminders_authorize` → user clicks OK on dialog
3. If `denied`: tell user to run `tccutil reset Reminders <bundle_id>` first,
   then call `reminders_authorize`
4. Verify with `reminders_status` → expect `authorized: true`

## Limitations

remindctl uses public EventKit APIs. These Reminders.app features are **not available**:
- Native sections, tags, smart lists
- File/image attachments
- Apple's private "Urgent" toggle
