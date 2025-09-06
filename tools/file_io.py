import os
import shutil
from datetime import datetime
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage


@tool
def write_file(filepath: str, content: str) -> str:
    """
    Writes or overwrites a file with the given content.
    Use with caution, as this will replace any existing content.
    If you want to modify a file, first read it, then provide the full new content here.

    Args:
        filepath: The absolute path to the file to be written.
        content: The content to write into the file.
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.isabs(filepath):
        return f"Error: File path must be absolute. You provided: {filepath}"
    
    try:
        # Ensure the directory exists
        dir_name = os.path.dirname(filepath)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote content to {filepath}"
    except Exception as e:
        return f"Error: An unexpected error occurred while writing the file: {e}"


def read_file(filepath: str) -> tuple[str | None, str | None]:
    """
    Reads the content of a specified file.

    Args:
        filepath: The absolute path to the file.

    Returns:
        A tuple containing the content (str) and an error message (str).
        If successful, the error message will be None.
        If failed, the content will be None.
    """
    if not os.path.isabs(filepath):
        return None, f"Error: File path must be absolute. You provided: {filepath}"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, None
    except FileNotFoundError:
        return None, f"Error: File not found at the specified path: {filepath}"
    except Exception as e:
        return None, f"Error: An unexpected error occurred while reading the file: {e}"

def add_file_to_kb(source_path: str, kb_dir: str = "knowledge_base") -> tuple[str | None, str | None]:
    """
    Copies a file from a source path to the knowledge base directory.

    Args:
        source_path: The absolute path of the file to be copied.
        kb_dir: The destination knowledge base directory.

    Returns:
        A tuple containing a success message and an error message.
    """
    if not os.path.isabs(source_path):
        return None, f"Error: Source file path must be absolute. You provided: {source_path}"
    
    if not os.path.exists(source_path):
        return None, f"Error: Source file not found at {source_path}"

    if not os.path.isdir(kb_dir):
        try:
            os.makedirs(kb_dir)
        except Exception as e:
            return None, f"Error: Could not create knowledge base directory at {kb_dir}. Reason: {e}"

    try:
        shutil.copy(source_path, kb_dir)
        filename = os.path.basename(source_path)
        return f"Successfully copied '{filename}' to the knowledge base.", None
    except Exception as e:
        return None, f"Error: Could not copy file. Reason: {e}"

def save_session_history(history: list, filepath: str) -> tuple[str | None, str | None]:
    """
    Saves the conversation history to a file.

    Args:
        history: A list of message objects from langchain.
        filepath: The absolute path to the file to be written.

    Returns:
        A tuple containing a success message and an error message.
    """
    if not os.path.isabs(filepath):
        return None, f"Error: File path must be absolute. You provided: {filepath}"

    try:
        dir_name = os.path.dirname(filepath)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(filepath, 'w', encoding='utf-8') as f:
            for msg in history:
                if isinstance(msg, HumanMessage):
                    f.write(f"--- HUMAN ---\n{msg.content}\n\n")
                elif isinstance(msg, AIMessage):
                    # Handle AIMessage with potential tool calls
                    if msg.tool_calls:
                        tool_info = "".join([f"Tool Call: {tc['name']}({tc['args']})\n" for tc in msg.tool_calls])
                        f.write(f"--- AI (Tool Call) ---\n{tool_info}\n{msg.content}\n\n")
                    else:
                        f.write(f"--- AI ---\n{msg.content}\n\n")
                else: # For system messages or other types
                    f.write(f"--- SYSTEM ---\n{msg.content}\n\n")
        return f"Successfully saved session to {filepath}", None
    except Exception as e:
        return None, f"Error: An unexpected error occurred while saving the session: {e}"