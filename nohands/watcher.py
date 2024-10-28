from pathlib import Path
from watchfiles import awatch
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Set, Dict, Optional
import pygit2
import logging
from . import git
from . import config
from .types import FileEvent

class ConfigWatcher:
    def __init__(
        self,
        watch_paths: Set[Path],
        repo_configs: Dict[Path, Path],  # maps config path -> git repo path
        author: pygit2.Signature,
        max_workers: Optional[int] = None
    ):
        self.watch_paths = watch_paths
        self.repo_configs = repo_configs
        self.author = author
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logging.getLogger("nohands.watcher")
        # Rate limiting dict: path -> last_handled_time
        self.last_handled: Dict[Path, float] = {}
        self.rate_limit = 1.0  # Minimum seconds between handling same file

    def _get_repo_for_path(self, path: Path) -> Optional[Path]:
        """Find the appropriate git repo for a given path."""
        for config_path, repo_path in self.repo_configs.items():
            if path.is_relative_to(config_path):
                return repo_path
        return None

    async def _handle_change(self, change_type: str, path: Path) -> None:
        """Handle a single file change event."""
        now = asyncio.get_event_loop().time()
        
        # Rate limiting check
        if path in self.last_handled:
            time_since_last = now - self.last_handled[path]
            if time_since_last < self.rate_limit:
                self.logger.debug(f"Rate limiting {path}, skipping")
                return

        self.last_handled[path] = now
        
        repo_path = self._get_repo_for_path(Path(path))
        if not repo_path:
            self.logger.warning(f"No repository configured for {path}")
            return

        event = FileEvent(
            path=Path(path),
            change_type=change_type,
            repo_path=repo_path,
            author=self.author
        )

        try:
            # Submit git operations to thread pool
            await asyncio.get_event_loop().run_in_executor(
                self.executor,
                git.handle_file_change,
                event
            )
        except Exception as e:
            self.logger.error(f"Error handling change for {path}: {e}")

    async def watch(self) -> None:
        """Main watch loop."""
        self.logger.info(f"Starting watch on paths: {self.watch_paths}")
        
        # !TODO - seems to dies here
        try:
            async for changes in awatch(*self.watch_paths):
                tasks = []
                for change_type, path in changes:
                    task = asyncio.create_task(
                        self._handle_change(change_type, Path(path))
                    )
                    tasks.append(task)
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            self.logger.error(f"Watch loop error: {e}")
            raise

    def __getattr__(self, attr):
        self.logger.info(self.__name__, str(attr))
