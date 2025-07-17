import os
from django.core.files.storage import default_storage

ENTRIES_DIR = "entries"

def list_entries():
    """
    Returns a list of all encyclopedia entry names (without .md extension).
    """
    try:
        return [f[:-3] for f in os.listdir(ENTRIES_DIR) if f.endswith(".md")]
    except FileNotFoundError:
        os.makedirs(ENTRIES_DIR, exist_ok=True)
        return []


def save_entry(title, content):
    """
    Saves an encyclopedia entry (overwrites if already exists).
    """
    os.makedirs(ENTRIES_DIR, exist_ok=True)
    filepath = os.path.join(ENTRIES_DIR, f"{title}.md")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def get_entry(title):
    """
    Retrieves an encyclopedia entry by title.
    Returns None if the entry doesn't exist.
    """
    try:
        with default_storage.open(f"{ENTRIES_DIR}/{title}.md") as f:
            return f.read().decode("utf-8")
    except FileNotFoundError:
        return None


def delete_entry(title):
    """
    Deletes an encyclopedia entry by title.
    Returns True if the file was deleted, False if it did not exist.
    """
    filepath = os.path.join(ENTRIES_DIR, f"{title}.md")
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def get_new_entry_template():
    """
    Returns a default markdown template for a new entry.
    """
    return "# New Encyclopedia Entry\n\nWrite your content here..."
