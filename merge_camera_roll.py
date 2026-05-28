#!/share/CACHEDEV1_DATA/.qpkg/Python3/opt/python3/bin/python3.12

from pathlib import Path
import stat
import sys
from datetime import datetime
import os
import subprocess
import json
from typing import Optional


class CameraRollAdder:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    # TODO Sometimes the created time of photo is wrong and is instead stored on System.Photo.DateTaken.
    # However, this that is only accessible via Windows API and is not easily accessible on Linux.
    def _get_created_time(self, photo) -> Optional[datetime]:
        """Get the created time of the photo"""

        # For mp4 video files, use ffprobe to get the creation time from metadata
        if photo.suffix.lower() in [".mp4"]:
            cmd = [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                photo,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            fmt = data.get("format", {})
            tags = fmt.get("tags", {})
            return datetime.fromisoformat(
                tags.get("creation_time").replace("Z)", "+00:00")
            )

        else:  # For other files, use the file system's created time
            stat = photo.stat()
            # Windows
            if sys.platform.startswith("win"):
                timestamp = stat.st_ctime
            # macOS
            elif hasattr(stat, "st_birthtime"):
                timestamp = stat.st_birthtime
            # Linux fallback
            else:
                timestamp = stat.st_mtime
            return datetime.fromtimestamp(timestamp)

    def _get_target_subfolder_name(self, photo) -> str:
        """Get the target subfolder name based on the created time of the photo"""
        created_time = self._get_created_time(photo)
        if created_time is None:
            self.logger.warning(
                f"Could not determine created time for {photo}, using 'unknown_date' as subfolder name"
            )
            return "unknown"
        else:
            return created_time.strftime("%Y-%m")

    def _is_supported_file(self, file):
        # Check if the file is a Google photo or video file based on its extension
        return file.suffix.lower() in [
            ".jpg",
            ".jpeg",
            ".png",
            ".mp4",
            ".mp",
            ".gif",
            ".heic",
        ]

    def _get_camera_roll_files(self):
        """Lazily yield all files from camera roll folders."""
        liu_camera_roll_folder = self.config.get("liu_camera_roll_folder")
        robby_camera_roll_folder = self.config.get("robby_camera_roll_folder")

        if self._folder_exists(liu_camera_roll_folder):
            for p in Path(liu_camera_roll_folder).rglob("*"):
                if p.is_file():
                    yield p
        if self._folder_exists(robby_camera_roll_folder):
            for p in Path(robby_camera_roll_folder).rglob("*"):
                if p.is_file():
                    yield p

    def _folder_exists(self, folder: str) -> bool:
        return (
            folder is not None
            and folder != ""
            and Path(folder).exists()
            and Path(folder).is_dir()
        )

    def add_photos_to_master_set(self):
        destination_photos_folder = self.config.get("destination_photos_folder")
        if not self._folder_exists(destination_photos_folder):
            self.logger.error(
                f"Did not merge camera roll. Destination photos folder does not exist: {destination_photos_folder}"
            )
            return
        destination_photos_folder = Path(destination_photos_folder)

        for file in self._get_camera_roll_files():
            if self._is_supported_file(file):
                target_subfolder = (
                    destination_photos_folder / self._get_target_subfolder_name(file)
                )
                try:
                    target_subfolder.mkdir(exist_ok=True)
                    target_photo = target_subfolder / file.name
                    if not target_photo.exists():
                        target_photo.write_bytes(file.read_bytes())
                        self.logger.debug(f"Copied {file} to {target_photo}")
                    else:
                        self.logger.debug(
                            f"Skipped {file} as it already exists in {target_photo}"
                        )
                except Exception as e:
                    self.logger.error(
                        f"Error occurred while creating target subfolder: {e}"
                    )
                    break

            else:
                self.logger.warning(
                    f"Skipped {file} as it is not a supported photo or video file"
                )
