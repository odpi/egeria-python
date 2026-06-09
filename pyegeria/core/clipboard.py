"""
Safe clipboard utility to handle pyperclip missing or failing.
"""
import logging

try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False
    logging.warning("pyperclip not found. Clipboard functionality will be disabled.")

def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to clipboard safely.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    if not HAS_PYPERCLIP:
        logging.error("Clipboard functionality is disabled because pyperclip is not installed.")
        return False
    
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        logging.error(f"Failed to copy to clipboard: {e}")
        return False

def get_from_clipboard() -> str | None:
    """
    Get text from clipboard safely.
    
    Returns:
        str | None: The text from clipboard, or None if failed.
    """
    if not HAS_PYPERCLIP:
        logging.error("Clipboard functionality is disabled because pyperclip is not installed.")
        return None
    
    try:
        return pyperclip.paste()
    except Exception as e:
        logging.error(f"Failed to paste from clipboard: {e}")
        return None
