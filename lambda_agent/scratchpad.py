"""
Scratchpad Module
=================
Provides tools for the agent to maintain a persistent, human-readable scratchpad
file (.lambda_scratchpad.md) in the user's working directory.

The scratchpad lets the agent plan complex tasks, track progress, and keep
implementation notes — all visible to the user as a markdown file in the repo.
"""

import os
from datetime import datetime

SCRATCHPAD_FILE = ".lambda_scratchpad.md"

_HEADER_TEMPLATE = """\
<!-- This file is managed by the Lambda coding agent. -->
<!-- Feel free to read it, but edits may be overwritten by the agent. -->

# Lambda Scratchpad

"""


def _ensure_scratchpad() -> str:
    """Return the absolute path to the scratchpad, creating it if it doesn't exist."""
    path = os.path.abspath(SCRATCHPAD_FILE)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(_HEADER_TEMPLATE)
    return path


def read_scratchpad() -> str:
    """Reads the full contents of the Lambda scratchpad file (.lambda_scratchpad.md).

    Use this to recall your previous plans, task lists, and implementation notes.
    """
    path = _ensure_scratchpad()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading scratchpad: {e}"


def write_scratchpad(content: str) -> str:
    """Overwrites the entire Lambda scratchpad file with the provided content.

    Use this when you need to replace the scratchpad with a fresh plan or when
    starting a new major task. For incremental updates, prefer update_scratchpad.

    Args:
        content: The full markdown content to write to the scratchpad.
    """
    path = _ensure_scratchpad()
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(_HEADER_TEMPLATE + content)
        return f"Scratchpad written successfully → {path}"
    except Exception as e:
        return f"Error writing scratchpad: {e}"


def update_scratchpad(note: str, section: str = "Notes") -> str:
    """Appends a timestamped note to a specific section in the scratchpad.

    This is ideal for incrementally logging progress, decisions, and discoveries
    without replacing existing content.

    Args:
        note: The text to append (supports markdown).
        section: The section heading to append under (e.g. 'Plan', 'Progress', 'Notes').
    """
    path = _ensure_scratchpad()
    try:
        with open(path, "r", encoding="utf-8") as f:
            existing = f.read()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n- **[{timestamp}]** {note}"

        section_heading = f"## {section}"
        if section_heading in existing:
            # Append under the existing section
            parts = existing.split(section_heading, 1)
            # Find the next section heading (##) or end of file
            rest = parts[1]
            next_section = rest.find("\n## ")
            if next_section == -1:
                # No next section — just append at the end
                updated = existing + entry
            else:
                # Insert before the next section
                insert_pos = len(parts[0]) + len(section_heading) + next_section
                updated = existing[:insert_pos] + entry + "\n" + existing[insert_pos:]
        else:
            # Create the section at the end
            updated = existing.rstrip() + f"\n\n{section_heading}\n{entry}\n"

        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)

        return f"Scratchpad updated (section: {section}) → {path}"
    except Exception as e:
        return f"Error updating scratchpad: {e}"


def clear_scratchpad() -> str:
    """Clears the scratchpad, resetting it to a blank state.

    Use this when a major task is fully complete and the scratchpad is no longer needed.
    """
    path = _ensure_scratchpad()
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(_HEADER_TEMPLATE)
        return f"Scratchpad cleared → {path}"
    except Exception as e:
        return f"Error clearing scratchpad: {e}"


# Tool registrations for the agent
SCRATCHPAD_EXECUTORS = {
    "read_scratchpad": read_scratchpad,
    "write_scratchpad": write_scratchpad,
    "update_scratchpad": update_scratchpad,
    "clear_scratchpad": clear_scratchpad,
}

SCRATCHPAD_FUNCTIONS = [
    read_scratchpad,
    write_scratchpad,
    update_scratchpad,
    clear_scratchpad,
]
