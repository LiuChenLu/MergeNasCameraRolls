#!/share/CACHEDEV1_DATA/.qpkg/Python3/opt/python3/bin/python3

import sys
import json
from pathlib import Path

"""
Example usage:
    python main.py /foo/config.json
"""


def check_files_exist(config):
    """Check if the files specified in the config exist. If not, print an error message and exit."""
    for key in [
        "liu_camera_roll_folder",
        "robby_camera_roll_folder",
        "destination_photos_folder",
    ]:
        path = config.get(key)
        if path is None:
            print(f"Error: Missing required configuration key: {key}", file=sys.stderr)
            sys.exit(1)
        if not Path(path).exists():
            print(f"Error: Path does not exist: {path}", file=sys.stderr)
            sys.exit(1)
    print("All specified paths exist.")


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

    check_files_exist(config)
    return config


def main():
    try:
        # Check for optional command-line argument for config path
        config_path = sys.argv[1] if len(sys.argv) > 1 else None
        config = load_config(config_path)
        print("Configuration loaded successfully:")
        print(json.dumps(config, indent=2))
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing config.json: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
    sys.exit(0)
