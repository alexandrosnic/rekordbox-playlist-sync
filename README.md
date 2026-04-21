# Rekordbox Playlist Sync

Syncs local m3u8 playlists into Rekordbox XML, deduplicates playlist entries, and can attempt best-effort UI automation for export/import steps.

## Entrypoint
- main.py

## Run
```pwsh
python3 main.py --auto-rekordbox
```

## Setup
```pwsh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# create local config from template
cp config/playlist_path.json.example config/playlist_path.json
```

Set your XML path in:
- config/playlist_path.json

Keep this local and uncommitted. Use `config/playlist_path.json.example` as the shareable template.

## Useful options
- --auto-rekordbox
- --full-auto
- --export-timeout 300
- --auto-import-ui

## Project structure
- app/
- utils/
- config/

This folder is self-contained and can be published as its own repository.

## Related repositories
- YouTube downloader: `git@github.com:alexandrosnic/youtube-playlist-downloader.git`
- Orchestration suite: `git@github.com:alexandrosnic/playlist-sync-suite.git`

If you want to run all projects together from a clean workspace:

```pwsh
mkdir playlist-sync-workspace
cd playlist-sync-workspace
git clone git@github.com:alexandrosnic/youtube-playlist-downloader.git youtube
git clone git@github.com:alexandrosnic/rekordbox-playlist-sync.git rekordbox
git clone git@github.com:alexandrosnic/playlist-sync-suite.git playlist_sync_suite
```

## Public safety checklist
- Never commit `config/playlist_path.json` (local machine paths).
- Commit only `config/playlist_path.json.example` as the shareable template.
