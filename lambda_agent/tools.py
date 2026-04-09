import subprocess
import os


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


# A dictionary mapping tool names to Python functions for dynamic execution
TOOL_EXECUTORS = {
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
    "get_workspace_summary": get_workspace_summary,
}

# The list of raw Python functions for the Gemini SDK to auto-generate schemas
TOOL_FUNCTIONS = [read_file, write_file, run_command, get_workspace_summary]
