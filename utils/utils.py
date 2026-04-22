import json
import os


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read_json(parent_dir, file_name):
    """Read a JSON file under this project root."""
    file_path = os.path.join(project_root, parent_dir, file_name)
    if not os.path.exists(file_path):
        example_file = f"{file_name}.example"
        example_path = os.path.join(project_root, parent_dir, example_file)
        if os.path.exists(example_path):
            raise FileNotFoundError(
                f"Config file not found: {file_path}\n"
                f"Please copy {example_path} to {file_path} and fill in your values."
            )
        raise FileNotFoundError(
            f"Config file not found: {file_path}\n"
            "Please create this file with the required configuration."
        )

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_sync_paths() -> dict:
    """Return path configuration for Rekordbox sync operations.

    Preferred key for source playlists:
    - sync_paths.source_playlist_m3u8_dir

    Backward-compatible legacy key:
    - sync_paths.youtube_playlist_m3u8_dir
    """
    config = read_json("config", "playlist_path.json")
    sync_paths = config["sync_paths"]

    if "source_playlist_m3u8_dir" not in sync_paths:
        legacy_key = "youtube_playlist_m3u8_dir"
        if legacy_key in sync_paths:
            sync_paths["source_playlist_m3u8_dir"] = sync_paths[legacy_key]
        else:
            raise KeyError(
                "Missing required config key in config/playlist_path.json: "
                "sync_paths.source_playlist_m3u8_dir"
            )

    return sync_paths
