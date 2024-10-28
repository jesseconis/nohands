# !TODO 
# - move from click to typer
# - check if bees hiding here?
# - dont lock invoking shell! daemonize or shell bg 
import asyncio
import logging
from pathlib import Path
import sys
from . import config
from . import watcher
import pygit2
import typer

app = typer.Typer()

@app.command()
def main(
    config_path: Path = typer.Option(
        Path.home() / ".config" / "nohands" / "config.toml",
        "--config",
        "-c",
        help="Path to config file",
        exists=True,
    ),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
) -> None:
    """Automatic config file watcher with git integration."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger("nohands")
    
    try:
        logger.info(f"Loading config from {config_path}")
        cfg = config.load_config(config_path)
        
        author = pygit2.Signature(
            cfg.author_name,
            cfg.author_email
        )
        
        logger.info("Starting config watcher")
        config_watcher = watcher.ConfigWatcher(
            watch_paths=cfg.watch_paths,
            repo_configs=cfg.repo_configs,
            author=author
        )
        
        asyncio.run(config_watcher.watch(),debug=True)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    app()
