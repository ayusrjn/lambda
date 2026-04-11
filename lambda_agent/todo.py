"""
Todo Module
===========
Provides tools for the agent to maintain a persistent, human-readable todo
file (.agent/todo.md) in the user's working directory.

The todo list lets the agent plan complex tasks and track progress, while
the scratchpad is used for free-form notes and discoveries.
"""

import os

AGENT_DIR = ".agent"
TODO_FILE = os.path.join(AGENT_DIR, "todo.md")

_HEADER_TEMPLATE = """\
<!-- This file is managed by the Lambda coding agent. -->
<!-- Feel free to read it, but edits may be overwritten by the agent. -->

# Lambda Task List

## To Do
"""


def _ensure_todo() -> str:
    """Return the absolute path to the todo list, creating it if it doesn't exist."""
    agent_dir = os.path.abspath(AGENT_DIR)
    os.makedirs(agent_dir, exist_ok=True)
    path = os.path.abspath(TODO_FILE)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(_HEADER_TEMPLATE)
    return path


def read_todo() -> str:
    """Reads the full contents of the Lambda todo file (.agent/todo.md).

    Use this to recall your current task list and implementation plan.
    """
    path = _ensure_todo()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading todo list: {e}"


def write_todo(content: str) -> str:
    """Overwrites the entire Lambda todo file with the provided content.

    Use this when you need to replace the todo list with a fresh task list.
    For incremental updates, prefer update_todo.

    Args:
        content: The full markdown content to write to the todo list.
    """
    path = _ensure_todo()
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(_HEADER_TEMPLATE + content)
        return f"Todo list written successfully → {path}"
    except Exception as e:
        return f"Error writing todo list: {e}"


def update_todo(note: str, section: str = "To Do") -> str:
    """Appends an item to a specific section in the todo list.

    This is ideal for checking off steps or adding new sub-tasks.

    Args:
        note: The text to append (supports markdown, e.g. '- [ ] Task').
        section: The section heading to append under (e.g. 'To Do', 'In Progress', 'Done').
    """
    path = _ensure_todo()
    try:
        with open(path, "r", encoding="utf-8") as f:
            existing = f.read()

        entry = f"\n{note}"

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

        return f"Todo list updated (section: {section}) → {path}"
    except Exception as e:
        return f"Error updating todo list: {e}"


def clear_todo() -> str:
    """Clears the todo list, resetting it to a blank state.

    Use this when a major task is fully complete and the task list is no longer needed.
    """
    path = _ensure_todo()
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(_HEADER_TEMPLATE)
        return f"Todo list cleared → {path}"
    except Exception as e:
        return f"Error clearing todo list: {e}"


# Tool registrations for the agent
TODO_EXECUTORS = {
    "read_todo": read_todo,
    "write_todo": write_todo,
    "update_todo": update_todo,
    "clear_todo": clear_todo,
}

TODO_FUNCTIONS = [
    read_todo,
    write_todo,
    update_todo,
    clear_todo,
]
