from dataclasses import dataclass
from pathlib import Path
import pygit2

@dataclass
class FileEvent:
    path: Path
    change_type: str
    repo_path: Path
    author: pygit2.Signature
