#!/share/CACHEDEV1_DATA/.qpkg/Python3/opt/python3/bin/python3.12

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from merge_camera_roll import CameraRollAdder

"""
Example usage:
    python main.py /foo/config.json
"""


def load_config(config_path=None):
    """Load configuration from config.json and check file paths listed in config exists.

    Args:
        config_path: Optional path to config.json. If not provided, uses config.json in the same directory as this script.
    """
    if config_path is None:
        config_path = Path(__file__).parent / "config.json"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        config = json.load(f)
    return config


def init_logger(logs_file):
    """Initialize logger to write logs to the specified logs_file."""
    if logs_file is None or logs_file == "" or not Path(logs_file).exists():
        print(f"Error: Logs file does not exist: {logs_file}", file=sys.stderr)
        sys.exit(1)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(logs_file)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def main():
    try:
        # Check for optional command-line argument for config path
        config_path = sys.argv[1] if len(sys.argv) > 1 else None
        config = load_config(config_path)
        logger = init_logger(config.get("logs_file"))

        # Log debug message for config read success
        if logger:
            logger.debug("Reading config success. Logger init success.")

        CameraRollAdder(config, logger).add_photos_to_master_set()

        # Log info message before exiting
        if logger:
            logger.info(
                f"Finished running camera roll merger, with config as {json.dumps(config)}"
            )

    except FileNotFoundError as e:
        print(f"Error: {e}. Config file not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing config.json from config file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
    sys.exit(0)
