# src/nohands/config.py
import tomli
from pathlib import Path
from typing import Dict, Set
import pygit2
from dataclasses import dataclass

@dataclass
class NohandsConfig:
    watch_paths: Set[Path]
    repo_configs: Dict[Path, Path]
    author_name: str
    author_email: str

def load_config(config_path: Path) -> NohandsConfig:
    """Load and parse configuration file."""
    with open(config_path, 'rb') as f:
        config_data = tomli.load(f)
    
    watch_paths = set()
    repo_configs = {}
    
    for watch_config in config_data.get('watch_paths', []):
        path = Path(watch_config['path']).expanduser()
        repo = Path(watch_config['git_repo']).expanduser()
        watch_paths.add(path)
        repo_configs[path] = repo
        
        # Initialize repo if it doesn't exist
        if not repo.exists():
            pygit2.init_repository(repo, initial_head='main')
    
    return NohandsConfig(
        watch_paths=watch_paths,
        repo_configs=repo_configs,
        author_name=config_data['author']['name'],
        author_email=config_data['author']['email']
    )
