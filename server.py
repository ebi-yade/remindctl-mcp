"""MCP server wrapping remindctl for Apple Reminders integration."""

import shlex
import subprocess
from mcp.server import FastMCP

REMINDCTL = "/opt/homebrew/bin/remindctl"

mcp = FastMCP("remindctl")


def _run(args: list[str]) -> str:
    result = subprocess.run(
        [REMINDCTL] + args, capture_output=True, text=True, timeout=15,
    )
    if result.returncode != 0:
        return f"Error (exit {result.returncode}):\n{result.stderr.strip() or result.stdout.strip()}"
    return result.stdout.strip()


@mcp.tool()
def reminders_authorize() -> str:
    """Trigger macOS Reminders permission dialog via osascript.

    Use when access is denied or not-determined. This forces a TCC prompt
    so the MCP host app (e.g. Amazon Quick) can obtain Reminders access.
    """
    r = subprocess.run(
        ["osascript", "-e", 'tell application "Reminders" to get name of every list'],
        capture_output=True, text=True, timeout=10,
    )
    return f"rc={r.returncode} out={r.stdout.strip()} err={r.stderr.strip()}"


@mcp.tool()
def reminders_status() -> str:
    """Check Reminders authorization status."""
    return _run(["status", "--json"])


@mcp.tool()
def reminders_show(filter: str = "today", reminder_list: str = "") -> str:
    """Show reminders by filter: today, tomorrow, week, overdue, upcoming, open, completed, all, or YYYY-MM-DD."""
    args = ["show", filter, "--json"]
    if reminder_list:
        args += ["--list", reminder_list]
    return _run(args)


@mcp.tool()
def reminders_search(query: str, reminder_list: str = "") -> str:
    """Search reminders by query string."""
    args = ["search", query, "--json"]
    if reminder_list:
        args += ["--list", reminder_list]
    return _run(args)


@mcp.tool()
def reminders_lists(names: str = "") -> str:
    """Show all reminder lists. Pass comma-separated names to show reminders in specific list(s)."""
    args = ["list"]
    if names:
        args += names.split(",")
    args.append("--json")
    return _run(args)


@mcp.tool()
def reminders_add(title: str, reminder_list: str = "", due: str = "", alarm: str = "",
                  notes: str = "", url: str = "", repeat: str = "", priority: str = "") -> str:
    """Create a new reminder."""
    args = ["add", title]
    for flag, val in [("--list", reminder_list), ("--due", due), ("--alarm", alarm),
                      ("--notes", notes), ("--url", url), ("--repeat", repeat),
                      ("--priority", priority)]:
        if val:
            args += [flag, val]
    args.append("--json")
    return _run(args)


@mcp.tool()
def reminders_edit(id: str, title: str = "", reminder_list: str = "", due: str = "",
                   clear_due: bool = False, alarm: str = "", clear_alarm: bool = False,
                   notes: str = "", url: str = "", clear_url: bool = False,
                   repeat: str = "", no_repeat: bool = False, priority: str = "") -> str:
    """Edit a reminder by index or ID prefix."""
    args = ["edit", id]
    for flag, val in [("--title", title), ("--list", reminder_list), ("--due", due),
                      ("--alarm", alarm), ("--notes", notes), ("--url", url),
                      ("--repeat", repeat), ("--priority", priority)]:
        if val:
            args += [flag, val]
    for flag, val in [("--clear-due", clear_due), ("--clear-alarm", clear_alarm),
                      ("--clear-url", clear_url), ("--no-repeat", no_repeat)]:
        if val:
            args.append(flag)
    args.append("--json")
    return _run(args)


@mcp.tool()
def reminders_complete(ids: str) -> str:
    """Mark reminders as complete. Pass comma-separated indexes or ID prefixes."""
    return _run(["complete"] + ids.split(",") + ["--json"])


@mcp.tool()
def reminders_delete(ids: str) -> str:
    """Delete reminders. Pass comma-separated indexes or ID prefixes."""
    return _run(["delete"] + ids.split(",") + ["--force", "--json"])


@mcp.tool()
def remindctl_raw(command: str) -> str:
    """Run any remindctl command directly. Fallback for operations not covered by other tools.

    Pass the full command string as you would on CLI (without 'remindctl' prefix).
    --json and --no-input are appended automatically.

    Examples: 'list Shopping --create', 'list OldList --delete --force', 'export --list Work --export-format csv'
    """
    args = shlex.split(command)
    # Append --json and --no-input if not already present
    if "--json" not in args:
        args.append("--json")
    if "--no-input" not in args:
        args.append("--no-input")
    return _run(args)


if __name__ == "__main__":
    mcp.run()
