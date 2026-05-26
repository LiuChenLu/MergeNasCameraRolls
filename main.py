#!/share/CACHEDEV1_DATA/.qpkg/Python3/opt/python3/bin/python3

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

"""
Example usage:
    python main.py /foo/config.json
"""


def check_files_exist(path, print_and_exit=False, logger=None):
    """Check if the files specified in the path exist. If not, print or log an error message and exit. If print_and_exit is True, program will exit."""
    if path is not None and Path(path).exists():
        return True

    if print_and_exit:
        print(f"Error: Missing file or path does not exist: {path}", file=sys.stderr)
        sys.exit(1)
    elif logger:
        logger.error(f"Error: Missing file or path does not exist: {path}")
    else:
        print(f"Error: Missing file or path does not exist: {path}", file=sys.stderr)

    return False


def load_config(config_path=None):
    """Load configuration from config.json

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
    for key in [
        "liu_camera_roll_folder",
        "robby_camera_roll_folder",
        "destination_photos_folder",
        "logs_file",
    ]:
        path = config.get(key)
        check_files_exist(path, print_and_exit=True)
    return config


def main():
    try:
        # Check for optional command-line argument for config path
        config_path = sys.argv[1] if len(sys.argv) > 1 else None
        config = load_config(config_path)

        # Set up logging with logs_file from config
        logs_file = config.get("logs_file")
        if logs_file and check_files_exist(logs_file, print_and_exit=True):
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler(logs_file)
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        else:
            logger = None

        # Log debug message for config read success
        if logger:
            logger.debug("reading config success")

        print("Configuration loaded successfully:")
        print(json.dumps(config, indent=2))

        # Log info message before exiting
        if logger:
            logger.info(
                f"successfully merged camera roll, with config as {json.dumps(config)}"
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
