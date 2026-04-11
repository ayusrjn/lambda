import subprocess
import os

from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich import box
from rich.console import Console

from .scratchpad import SCRATCHPAD_EXECUTORS, SCRATCHPAD_FUNCTIONS
from .subagent import SUBAGENT_EXECUTORS, SUBAGENT_FUNCTIONS

# Use the same console as the rest of the app if available; else create one
try:
    from .spinner import console
except ImportError:
    console = Console()


def read_file(path: str) -> str:
    """Reads the contents of a file.

    Args:
        path: The absolute or relative path to the file.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {path}: {str(e)}"


def write_file(path: str, content: str) -> str:
    """Writes content to a specific file path.

    Args:
        path: The path to the file to write.
        content: The text content to write to the file.
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing to file {path}: {str(e)}"


def run_command(command: str) -> str:
    """Executes a shell command on the host system.

    Args:
        command: The shell command to execute.
    """
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr
        return output if output else "Command executed successfully with no output."
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"


def get_workspace_summary() -> str:
    """Gathers git context, branch, status, recent commits, and project documentation (like README.md or rule files) to help the agent understand the whole project."""
    summary_parts = []

    # 1. Gather Git Context
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"], text=True, stderr=subprocess.STDOUT
        ).strip()
        status = subprocess.check_output(
            ["git", "status", "-s"], text=True, stderr=subprocess.STDOUT
        )
        log = subprocess.check_output(
            ["git", "log", "-n", "5", "--oneline"], text=True, stderr=subprocess.STDOUT
        )

        summary_parts.append(
            f"### Git Context\n**Branch**: {branch}\n**Status**:\n{status if status else 'Clean'}\n**Recent Commits**:\n{log}"
        )
    except Exception:
        summary_parts.append("### Git Context\nNot a git repository or git error.")

    # 2. Gather Directory Structure (limited to root)
    try:
        files = os.listdir(".")
        summary_parts.append(f"### Root Directory Files\n{', '.join(files)}")
    except Exception as e:
        summary_parts.append(f"### Directory Listing Error\n{e}")

    # 3. Read important docs
    docs_to_check = [
        "README.md",
        "README",
        ".cursorrules",
        ".agentrules",
        ".agent/scratchpad.md",
        "pyproject.toml",
        "package.json",
    ]
    for doc in docs_to_check:
        if os.path.exists(doc) and os.path.isfile(doc):
            try:
                with open(doc, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Truncate to save tokens if massive
                    if len(content) > 3000:
                        content = content[:3000] + "\n...[TRUNCATED]"
                    summary_parts.append(f"### Document: {doc}\n```\n{content}\n```")
            except Exception:
                pass

    return "\n\n".join(summary_parts)


def search_repo(query: str, path: str = ".") -> str:
    """Searches for a specific string query across all text files in the repository.

    Args:
        query: The substring to search for.
        path: The directory path to search within (defaults to current directory '.').
    """
    try:
        # Use grep for faster searching.
        # -r: recursive, -n: line numbers, -I: ignore binary files
        # -F: fixed strings (prevents regex injection if query has special chars)
        command = [
            "grep",
            "-rnIF",
            "--exclude-dir=.git",
            "--exclude-dir=.venv",
            "--exclude-dir=venv",
            "--exclude-dir=env",
            "--exclude-dir=__pycache__",
            "--exclude-dir=node_modules",
            "--exclude-dir=.ruff_cache",
            "--",
            query,
            path,
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            # grep output is already in the format we want (file:line: content)
            # but we strip it to clean it up lightly
            results = result.stdout.strip().split("\n")
            if not results or not results[0]:
                return f"No matches found for '{query}'"

            if len(results) > 100:
                return (
                    "\n".join(results[:100])
                    + f"\n\n... and {len(results) - 100} more matches."
                )
            return "\n".join(results)
        elif result.returncode == 1:
            return f"No matches found for '{query}'"
        else:
            return f"Error searching repository: {result.stderr.strip()}"
    except FileNotFoundError:
        return "Error: 'grep' is not installed or available in PATH."
    except Exception as e:
        return f"Error executing search: {str(e)}"


def ask_user(question: str) -> str:
    """Asks the user a clarifying question and returns their answer.

    Args:
        question: The question to ask the user.
    """
    try:
        console.print()
        console.print(
            Panel(
                Text(question, style="bold white"),
                border_style="yellow",
                box=box.ROUNDED,
                title=Text(" 🤔 Lambda asks ", style="bold black on bright_yellow"),
                title_align="left",
                padding=(0, 2),
            )
        )
        answer = Prompt.ask(
            "[bold bright_yellow]  Your answer[/bold bright_yellow]",
            console=console,
        )
        return answer
    except Exception as e:
        return f"Error asking user: {str(e)}"


# A dictionary mapping tool names to Python functions for dynamic execution
TOOL_EXECUTORS = {
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
    "search_repo": search_repo,
    "ask_user": ask_user,
    **SCRATCHPAD_EXECUTORS,
    **SUBAGENT_EXECUTORS,
}

# The list of raw Python functions for the Gemini SDK to auto-generate schemas
TOOL_FUNCTIONS = [
    read_file,
    write_file,
    run_command,
    search_repo,
    ask_user,
    *SCRATCHPAD_FUNCTIONS,
    *SUBAGENT_FUNCTIONS,
]
