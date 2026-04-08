import os
import subprocess

def read_file(path: str) -> str:
    """Reads the contents of a file.
    
    Args:
        path: The absolute or relative path to the file.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
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
        with open(path, 'w', encoding='utf-8') as f:
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
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        return output if output else "Command executed successfully with no output."
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"

# A dictionary mapping tool names to Python functions for dynamic execution
TOOL_EXECUTORS = {
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
}

# The list of raw Python functions for the Gemini SDK to auto-generate schemas
TOOL_FUNCTIONS = [read_file, write_file, run_command]