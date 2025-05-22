"""
Tool for displaying directory structure using the 'tree' command.
"""
import subprocess
import logging
import os
import platform
from google.generativeai.types import FunctionDeclaration, Tool

from .base import BaseTool

log = logging.getLogger(__name__)

# Determine the operating system
IS_WINDOWS = platform.system() == "Windows"

DEFAULT_TREE_DEPTH = 3
MAX_TREE_DEPTH = 10

class TreeTool(BaseTool):
    name: str = "tree"
    description: str = (
        f"""Displays the directory structure as a tree. Shows directories and files.
        Use this to understand the hierarchy and layout of the current working directory or a subdirectory.
        Defaults to a depth of {DEFAULT_TREE_DEPTH}. Use the 'depth' argument to specify a different level.
        Optionally specify a 'path' to view a subdirectory instead of the current directory."""
    )
    args_schema: dict = {
         "path": {
            "type": "string",
            "description": "Optional path to a specific directory relative to the workspace root. If omitted, uses the current directory.",
        },
        "depth": {
            "type": "integer",
            "description": f"Optional maximum display depth of the directory tree (Default: {DEFAULT_TREE_DEPTH}, Max: {MAX_TREE_DEPTH}).",
        },
    }
    # Optional args: path, depth
    required_args: list[str] = []

    def execute(self, path: str | None = None, depth: int | None = None) -> str:
        """Executes the tree command or equivalent based on OS."""
        
        if depth is None:
            depth_limit = DEFAULT_TREE_DEPTH
        else:
            # Clamp depth to be within reasonable limits
            depth_limit = max(1, min(depth, MAX_TREE_DEPTH))
        
        # Add path if specified
        target_path = "." # Default to current directory
        if path:
            # Basic path validation/sanitization might be needed depending on security context
            target_path = path
        
        # Configure command based on OS
        if IS_WINDOWS:
            # On Windows, tree command has different syntax
            command = ['tree', target_path]
            if depth_limit > 1:  # Windows tree doesn't have depth limit, but we can simulate it
                log.info(f"Windows tree doesn't support depth limit directly, showing full tree")
            log.info(f"Executing Windows tree command: {' '.join(command)}")
        else:
            # Unix/Linux tree command
            command = ['tree', f'-L', f'{depth_limit}', target_path]
            log.info(f"Executing Unix tree command: {' '.join(command)}")
        
        try:
            # Using shell=True for Windows to ensure the command works properly
            process = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                check=False, # Don't raise exception on non-zero exit code
                timeout=15, # Add a timeout
                shell=IS_WINDOWS # Use shell on Windows
            )

            if process.returncode == 0:
                log.info(f"Tree command successful for path '{target_path}' with depth {depth_limit}.")
                # Limit output size? Tree can be huge.
                output = process.stdout.strip()
                if len(output.splitlines()) > 200: # Limit lines as a proxy for size
                     log.warning(f"Tree output for '{target_path}' exceeded 200 lines. Truncating.")
                     output = "\n".join(output.splitlines()[:200]) + "\n... (output truncated)"
                return output
            elif process.returncode == 127 or "command not found" in process.stderr.lower():
                 log.error(f"\'tree\' command not found. It might not be installed.")
                 return "Error: 'tree' command not found. Please ensure it is installed and in the system's PATH."
            else:
                log.error(f"Tree command failed with return code {process.returncode}. Path: '{target_path}', Depth: {depth_limit}. Stderr: {process.stderr.strip()}")
                error_detail = process.stderr.strip() if process.stderr else "(No stderr)"
                return f"Error executing tree command (Code: {process.returncode}): {error_detail}"

        except FileNotFoundError:
             log.error(f"\'tree\' command not found (FileNotFoundError). It might not be installed.")
             # Provide more helpful message for Windows users
             if IS_WINDOWS:
                 return "Error: 'tree' command not found. This is a built-in Windows command, so this may indicate a system issue."
             else:
                 return "Error: 'tree' command not found. Please install it using your package manager (e.g., 'apt-get install tree' on Debian/Ubuntu)."
        except subprocess.TimeoutExpired:
             log.error(f"Tree command timed out for path '{target_path}' after 15 seconds.")
             return f"Error: Tree command timed out for path '{target_path}'. The directory might be too large or complex."
        except Exception as e:
            log.exception(f"An unexpected error occurred while executing tree command for path '{target_path}': {e}")
            return f"An unexpected error occurred while executing tree: {str(e)}" 