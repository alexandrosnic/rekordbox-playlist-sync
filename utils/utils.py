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
    """Return neutral path configuration for Rekordbox sync operations."""
    config = read_json("config", "playlist_path.json")
    return config["sync_paths"]
