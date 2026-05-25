from pathlib import Path
import stat
import sys
from datetime import datetime
import os
import subprocess
import json
from typing import Optional


class CameraRollAdder:
    def __init__(self):
        script_dir = Path(__file__).parent
        self.source_folder = script_dir / "Files" / "camera_roll_test" / "src"
        self.target_folder = script_dir / "Files" / "camera_roll_test" / "dest"

    # TODO known issue, sometimes the created time of photo is wrong. Should use System.Photo.DateTaken but i am on linux and can't be bothered.
    def get_created_time(self, photo) -> Optional[datetime]:
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

    def get_target_subfolder_name(self, photo) -> str:
        """Get the target subfolder name based on the created time of the photo"""
        created_time = self.get_created_time(photo)
        if created_time is None:
            print(
                f"\033[93mWarning: Could not determine created time for {photo}, using 'unknown_date' as subfolder name\033[0m"
            )
            return "unknown"
        else:
            return created_time.strftime("%Y-%m")

    def is_photo_file(self, file):
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

    def add_photos_to_master_set(self):
        for file in [p for p in self.source_folder.rglob("*") if p.is_file()]:
            if self.is_photo_file(file):
                target_subfolder = self.target_folder / self.get_target_subfolder_name(
                    file
                )
                print(f"Target subfolder: {target_subfolder}")

                try:
                    target_subfolder.mkdir(exist_ok=True)
                    target_photo = target_subfolder / file.name
                    if not target_photo.exists():
                        target_photo.write_bytes(file.read_bytes())
                        print(f"Copied {file} to {target_photo}")
                    else:
                        print(f"Skipped {file} as it already exists in {target_photo}")
                except Exception as e:
                    print(
                        f"\033[91mError occurred while creating target subfolder: {e }\033[0m"
                    )
                    break

            else:
                print(
                    f"\033[93mWarning: Skipped {file} as it is not a photo or video file\033[0m"
                )
