# src/nohands/git.py
import pygit2
from pathlib import Path
import logging
from typing import Optional
from .types import FileEvent

logger = logging.getLogger("nohands.git")

def handle_file_change(event: FileEvent) -> None:
    """Handle git operations for a file change event."""
    try:
        repo = pygit2.Repository(event.repo_path)
        relative_path = event.path.relative_to(event.path.parent)
        
        if event.change_type in ["added", "modified"]:
            # Read file content
            with open(event.path, 'rb') as f:
                content = f.read()
            
            # Create or update file in git
            blob_id = repo.create_blob(content)
            
            # Get the latest commit
            parent = repo.head.peel(pygit2.Commit) if not repo.is_empty else None
            
            # Prepare the tree
            builder = repo.TreeBuilder(parent.tree if parent else None)
            builder.insert(str(relative_path), blob_id, pygit2.GIT_FILEMODE_BLOB)
            tree_id = builder.write()
            
            # Create commit
            message = f"Update {relative_path} via nohands"
            if parent:
                repo.create_commit(
                    'HEAD',
                    event.author,
                    event.author,
                    message,
                    tree_id,
                    [parent.id]
                )
            else:
                repo.create_commit(
                    'HEAD',
                    event.author,
                    event.author,
                    message,
                    tree_id,
                    []
                )
                
            logger.info(f"Committed changes for {event.path}")
            
        elif event.change_type == "deleted":
            # Handle file deletion if needed
            # Similar to above but remove file from tree
            # !TODO
            pass
            
    except Exception as e:
        logger.error(f"Git operation failed for {event.path}: {e}")
        raise
