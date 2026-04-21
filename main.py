"""CLI entrypoint for the Rekordbox sync sub-project."""

import argparse

from app.rekordbox_handler import remove_duplicates, create_m3u8_playlists_from_xml
from app.rekordbox_automation import (
    backup_rekordbox_xml,
    delete_all_playlists_from_xml,
    import_m3u8_playlists_to_xml,
    import_rekordbox_playlists_to_xml,
    full_automated_workflow,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Rekordbox sync only.")
    parser.add_argument(
        "--auto-rekordbox",
        dest="auto_rekordbox",
        action="store_true",
        help="Run Rekordbox XML-only automation: backup, delete old playlists, and import new ones.",
    )
    parser.add_argument(
        "--full-auto",
        dest="full_auto",
        action="store_true",
        help=(
            "Run best-effort Rekordbox automation, including UI export/import "
            "attempts and XML update monitoring."
        ),
    )
    parser.add_argument(
        "--export-timeout",
        dest="export_timeout",
        type=int,
        default=300,
        help="Seconds to wait for Rekordbox XML export file update in full-auto mode.",
    )
    parser.add_argument(
        "--auto-import-ui",
        dest="auto_import_ui",
        action="store_true",
        help="In full-auto mode, also try to trigger Rekordbox XML import via UI automation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.full_auto:
        full_automated_workflow(
            wait_for_export=True,
            auto_import=args.auto_import_ui,
            export_timeout=args.export_timeout,
        )
        return

    if args.auto_rekordbox:
        print("\n=== Running automated Rekordbox XML workflow ===")
        backup_rekordbox_xml()
        remove_duplicates()
        create_m3u8_playlists_from_xml()
        delete_all_playlists_from_xml()
        import_m3u8_playlists_to_xml()
        import_rekordbox_playlists_to_xml()
        print("\n=== Automated Rekordbox XML workflow complete ===")
        print("Next: Import the XML into Rekordbox (File > Import > Import Playlist from XML)")
        return

    remove_duplicates()
    create_m3u8_playlists_from_xml()


if __name__ == "__main__":
    main()
