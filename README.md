# Rekordbox Playlist Sync

Syncs local m3u8 playlists into Rekordbox XML, deduplicates playlist entries, and can attempt best-effort UI automation for export/import steps.

This project can run on its own, or be coupled with the YouTube downloader project if you want to sync your YouTube playlists into Rekordbox.
It does not require YouTube playlists specifically; any `.m3u8` source playlists can be used.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

cp config/playlist_path.json.example config/playlist_path.json
```

## Required config values
- `sync_paths.source_playlist_m3u8_dir`: folder containing source `.m3u8` playlists
- `sync_paths.rekordbox_custom_playlists_m3u8_dir`: folder where Rekordbox-specific `.m3u8` playlists are written
- `sync_paths.xml_library_path`: path to your Rekordbox XML library file (this project reads and updates Rekordbox XML)

Backward compatibility: `sync_paths.youtube_playlist_m3u8_dir` is still accepted if you already use the older key name.

## Run
```bash
python3 main.py
```

## CLI options
- no flags: remove duplicate track entries in the Rekordbox XML and export playlists from the `rekordboxPlaylists` XML node into `.m3u8` files
- `--auto-rekordbox`: XML-only automated flow (backup XML, clean/rebuild playlists in XML)
- `--full-auto`: best-effort full automation including Rekordbox UI export/import attempts
- `--export-timeout 300`: wait time (seconds) for XML export update detection in `--full-auto`
- `--auto-import-ui`: with `--full-auto`, also attempt UI-triggered XML import

## Related repositories
- YouTube downloader: `https://github.com/alexandrosnic/youtube-playlist-downloader`
- Orchestration suite: `https://github.com/alexandrosnic/playlist-sync-suite`
- This repository: `https://github.com/alexandrosnic/rekordbox-playlist-sync`

## Notes
- Keep `config/playlist_path.json` local and uncommitted
- Commit only `config/playlist_path.json.example` as the template
