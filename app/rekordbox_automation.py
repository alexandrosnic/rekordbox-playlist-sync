"""Automation helpers for Rekordbox XML maintenance and optional UI automation.

The XML editing functions are deterministic and fully scriptable.
UI operations (export/import clicks inside Rekordbox) are best-effort and optional,
because Rekordbox does not expose an official automation API for those actions.
"""

import xml.etree.ElementTree as ET
from utils.utils import read_json, get_sync_paths
import os
import shutil
from datetime import datetime
import time


def _load_pyautogui():
    """Return pyautogui if installed, otherwise None."""
    try:
        import pyautogui  # type: ignore

        pyautogui.FAILSAFE = True
        return pyautogui
    except Exception:
        return None


def backup_rekordbox_xml():
    """
    Step 0: Backup the current latest.xml with a timestamp.
    Returns the backup file path.
    """
    sync_paths = get_sync_paths()
    rekordbox_xml = sync_paths["xml_library_path"]
    
    if not os.path.exists(rekordbox_xml):
        raise FileNotFoundError(f"Rekordbox XML not found: {rekordbox_xml}")
    
    # Create backup with timestamp
    xml_dir = os.path.dirname(rekordbox_xml)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"latest_backup_{timestamp}.xml"
    backup_path = os.path.join(xml_dir, backup_name)
    
    shutil.copy2(rekordbox_xml, backup_path)
    print(f"Backed up rekordbox XML to: {backup_path}")
    return backup_path


def watch_for_rekordbox_export(timeout=300, poll_seconds=1.0):
    """
    Watch the configured Rekordbox XML and return True when its mtime changes.
    Useful when export is still done manually in the UI.
    """
    sync_paths = get_sync_paths()
    rekordbox_xml = sync_paths["xml_library_path"]

    if not os.path.exists(rekordbox_xml):
        print(f"Cannot watch export. XML file does not exist: {rekordbox_xml}")
        return False

    start_mtime = os.path.getmtime(rekordbox_xml)
    start = time.time()

    while time.time() - start < timeout:
        try:
            current_mtime = os.path.getmtime(rekordbox_xml)
            if current_mtime > start_mtime:
                print("Detected Rekordbox XML export/update.")
                return True
        except FileNotFoundError:
            # File may be temporarily replaced while exporting.
            pass
        time.sleep(poll_seconds)

    print("Timed out waiting for Rekordbox XML export/update.")
    return False


def automate_rekordbox_export(pre_delay_seconds=2.0):
    """
    Best-effort UI automation for Rekordbox export using keyboard shortcuts.
    Returns True when commands were sent, False when unavailable/failing.
    """
    pyautogui = _load_pyautogui()
    if pyautogui is None:
        print("pyautogui not installed. Skipping automatic export click automation.")
        return False

    print("Attempting Rekordbox export UI automation (best effort).")
    print("Make sure Rekordbox window is focused and no modal dialogs are open.")

    try:
        time.sleep(pre_delay_seconds)
        # Typical menu access path: Alt+F then export/import shortcuts vary by version.
        # We send only conservative key combos and rely on file watcher verification.
        pyautogui.hotkey("alt", "f")
        time.sleep(0.3)
        pyautogui.press("x")
        time.sleep(0.3)
        pyautogui.press("enter")
        return True
    except Exception as exc:
        print(f"UI export automation failed: {exc}")
        return False


def set_rekordbox_xml_preference():
    """
    Validate the XML path referenced by this project.

    Rekordbox preference switching is not officially scriptable. We therefore
    verify the file exists and report what path Rekordbox should point to.
    """
    sync_paths = get_sync_paths()
    rekordbox_xml = sync_paths["xml_library_path"]

    if os.path.exists(rekordbox_xml):
        print(f"XML preference target is ready: {rekordbox_xml}")
    else:
        raise FileNotFoundError(
            "Configured Rekordbox XML path does not exist. "
            f"Expected: {rekordbox_xml}"
        )

    print(
        "If Rekordbox is not already pointed to this file, set it once in "
        "Preferences > Advanced > rekordbox.xml."
    )


def trigger_rekordbox_import(pre_delay_seconds=2.0):
    """
    Best-effort UI automation to trigger 'Import Playlist from XML'.
    Returns True when key commands were sent.
    """
    pyautogui = _load_pyautogui()
    if pyautogui is None:
        print("pyautogui not installed. Skipping automatic import click automation.")
        return False

    print("Attempting Rekordbox import UI automation (best effort).")
    print("Make sure Rekordbox window is focused and no modal dialogs are open.")

    try:
        time.sleep(pre_delay_seconds)
        pyautogui.hotkey("alt", "f")
        time.sleep(0.3)
        pyautogui.press("i")
        time.sleep(0.3)
        pyautogui.press("enter")
        return True
    except Exception as exc:
        print(f"UI import automation failed: {exc}")
        return False


def export_rekordbox_xml_from_database():
    """
    Placeholder for DB-level export.

    Rekordbox database format is not stable/publicly documented for writing an
    XML export safely. We keep this as a no-op and rely on UI export/watching.
    """
    print(
        "Database-level XML export is not supported. "
        "Use UI export automation or manual export."
    )
    return False


def delete_all_playlists_from_xml():
    """
    Step 4: Delete all playlists from the rekordbox XML (except rekordboxPlaylists).
    This replaces the manual deletion step.
    """
    sync_paths = get_sync_paths()
    rekordbox_xml = sync_paths["xml_library_path"]
    
    tree = ET.parse(rekordbox_xml)
    root = tree.getroot()
    
    playlists_node = root.find('PLAYLISTS')
    if playlists_node is None:
        print("No PLAYLISTS node found in XML")
        return
    
    # Remove all top-level NODE elements (playlists) except rekordboxPlaylists
    nodes_to_remove = []
    for node in playlists_node.findall('NODE'):
        node_name = node.get('Name', '')
        # Keep rekordboxPlaylists, remove everything else
        if node_name != 'rekordboxPlaylists':
            nodes_to_remove.append(node)
    
    for node in nodes_to_remove:
        playlists_node.remove(node)
        print(f"Removed playlist: {node.get('Name', 'Unknown')}")
    
    tree.write(rekordbox_xml, encoding='UTF-8', xml_declaration=True)
    print(f"Deleted {len(nodes_to_remove)} playlists from XML")


def import_m3u8_playlists_to_xml():
    """
    Step 5: Import all m3u8 playlists from the playlist folder into rekordbox XML.
    This replaces the manual import step.
    """
    sync_paths = get_sync_paths()
    rekordbox_xml = sync_paths["xml_library_path"]
    playlist_m3u8_folder = sync_paths["youtube_playlist_m3u8_dir"]
    
    tree = ET.parse(rekordbox_xml)
    root = tree.getroot()
    
    # Get or create PLAYLISTS node
    playlists_node = root.find('PLAYLISTS')
    if playlists_node is None:
        playlists_node = ET.SubElement(root, 'PLAYLISTS')
    
    # Build track location map from existing collection
    track_locations = {}
    collection = root.find('COLLECTION')
    if collection is not None:
        for track in collection.findall('TRACK'):
            track_id = track.get("TrackID")
            location = track.get("Location", "")
            # Normalize location
            location = location.replace("file://localhost", "").replace("%20", " ")
            track_locations[location.lower()] = track_id
    
    # Find all m3u8 files
    m3u8_files = []
    if os.path.exists(playlist_m3u8_folder):
        for file in os.listdir(playlist_m3u8_folder):
            if file.endswith('.m3u8'):
                m3u8_files.append(os.path.join(playlist_m3u8_folder, file))
    
    imported_count = 0
    for m3u8_path in m3u8_files:
        playlist_name = os.path.splitext(os.path.basename(m3u8_path))[0]
        
        # Skip if playlist already exists (to avoid duplicates)
        existing = playlists_node.find(f".//NODE[@Name='{playlist_name}']")
        if existing is not None:
            print(f"Playlist '{playlist_name}' already exists, skipping")
            continue
        
        # Read m3u8 file
        track_paths = []
        with open(m3u8_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    track_paths.append(line)
        
        # Create playlist node
        playlist_node = ET.SubElement(playlists_node, 'NODE')
        playlist_node.set('Name', playlist_name)
        playlist_node.set('Type', '1')  # Type 1 = playlist
        playlist_node.set('Entries', str(len(track_paths)))
        
        # Add tracks to playlist
        for track_path in track_paths:
            # Normalize path for lookup
            track_path_normalized = track_path.replace("\\", "/").lower()
            
            # Find track ID by matching location
            track_id = None
            for location, tid in track_locations.items():
                if location.endswith(track_path_normalized) or track_path_normalized.endswith(location):
                    track_id = tid
                    break
            
            if track_id:
                track_elem = ET.SubElement(playlist_node, 'TRACK')
                track_elem.set('Key', track_id)
            else:
                print(f"Warning: Track not found in collection: {track_path}")
        
        imported_count += 1
        print(f"Imported playlist: {playlist_name} ({len(track_paths)} tracks)")
    
    tree.write(rekordbox_xml, encoding='UTF-8', xml_declaration=True)
    print(f"Imported {imported_count} playlists to XML")


def import_rekordbox_playlists_to_xml():
    """
    Step 6: Import rekordboxPlaylists from m3u8 files.
    This is similar to step 5 but for the custom rekordboxPlaylists folder.
    """
    sync_paths = get_sync_paths()
    rekordbox_xml = sync_paths["xml_library_path"]
    custom_playlist_folder = sync_paths["rekordbox_custom_playlists_m3u8_dir"]
    
    tree = ET.parse(rekordbox_xml)
    root = tree.getroot()
    
    # Get or create rekordboxPlaylists node
    playlists_node = root.find('PLAYLISTS')
    if playlists_node is None:
        playlists_node = ET.SubElement(root, 'PLAYLISTS')
    
    rekordbox_playlists_node = playlists_node.find(".//NODE[@Name='rekordboxPlaylists']")
    if rekordbox_playlists_node is None:
        rekordbox_playlists_node = ET.SubElement(playlists_node, 'NODE')
        rekordbox_playlists_node.set('Name', 'rekordboxPlaylists')
        rekordbox_playlists_node.set('Type', '0')  # Type 0 = folder
    
    # Build track location map
    track_locations = {}
    collection = root.find('COLLECTION')
    if collection is not None:
        for track in collection.findall('TRACK'):
            track_id = track.get("TrackID")
            location = track.get("Location", "")
            location = location.replace("file://localhost", "").replace("%20", " ")
            track_locations[location.lower()] = track_id
    
    # Find all m3u8 files in custom folder
    m3u8_files = []
    if os.path.exists(custom_playlist_folder):
        for file in os.listdir(custom_playlist_folder):
            if file.endswith('.m3u8'):
                m3u8_files.append(os.path.join(custom_playlist_folder, file))
    
    imported_count = 0
    for m3u8_path in m3u8_files:
        playlist_name = os.path.splitext(os.path.basename(m3u8_path))[0]
        
        # Skip if already exists
        existing = rekordbox_playlists_node.find(f".//NODE[@Name='{playlist_name}']")
        if existing is not None:
            print(f"Playlist '{playlist_name}' already exists in rekordboxPlaylists, skipping")
            continue
        
        # Read m3u8 file
        track_paths = []
        with open(m3u8_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    track_paths.append(line)
        
        # Create playlist node under rekordboxPlaylists
        playlist_node = ET.SubElement(rekordbox_playlists_node, 'NODE')
        playlist_node.set('Name', playlist_name)
        playlist_node.set('Type', '1')
        playlist_node.set('Entries', str(len(track_paths)))
        
        # Add tracks
        for track_path in track_paths:
            track_path_normalized = track_path.replace("\\", "/").lower()
            track_id = None
            for location, tid in track_locations.items():
                if location.endswith(track_path_normalized) or track_path_normalized.endswith(location):
                    track_id = tid
                    break
            
            if track_id:
                track_elem = ET.SubElement(playlist_node, 'TRACK')
                track_elem.set('Key', track_id)
        
        imported_count += 1
        print(f"Imported rekordboxPlaylist: {playlist_name} ({len(track_paths)} tracks)")
    
    tree.write(rekordbox_xml, encoding='UTF-8', xml_declaration=True)
    print(f"Imported {imported_count} rekordboxPlaylists to XML")


def full_automated_workflow(wait_for_export=True, auto_import=False, export_timeout=300):
    """
    Run the FULLY automated workflow including ALL steps.
    
    :param wait_for_export: If True, wait for manual rekordbox export (watches file)
    :param auto_import: If True, attempt to automate rekordbox import (requires pyautogui)
    """
    print("=== Starting FULLY automated rekordbox workflow ===")
    sync_paths = get_sync_paths()
    
    # Step 0: Backup
    backup_path = backup_rekordbox_xml()
    
    # Step 1: Export (automate or wait for it)
    print("\n--- Step 1: Exporting from rekordbox ---")
    if wait_for_export:
        # Try GUI automation first
        if not automate_rekordbox_export():
            # Fall back to file watcher if automation fails
            print("GUI automation failed, waiting for manual export...")
            if not watch_for_rekordbox_export(timeout=export_timeout):
                print("Warning: Rekordbox export not detected. Continuing anyway...")
        elif not watch_for_rekordbox_export(timeout=export_timeout):
            print("Warning: Export command sent but no file update detected.")
    else:
        # Try to export from database (experimental)
        export_rekordbox_xml_from_database()
    
    # Step 2: Set preferences
    print("\n--- Step 2: Setting rekordbox XML preference ---")
    set_rekordbox_xml_preference()
    
    # Step 3: Run main sync (this is done by main.py, so we skip it here)
    print("\n--- Step 3: Run main.py separately (or it's already done) ---")
    
    # Step 4: Delete old playlists
    print("\n--- Step 4: Deleting old playlists from XML ---")
    delete_all_playlists_from_xml()
    
    # Step 5: Import m3u8 playlists
    print("\n--- Step 5: Importing m3u8 playlists to XML ---")
    import_m3u8_playlists_to_xml()
    
    # Step 6: Import rekordboxPlaylists
    print("\n--- Step 6: Importing rekordboxPlaylists to XML ---")
    import_rekordbox_playlists_to_xml()
    
    # Step 6b: Trigger rekordbox import
    if auto_import:
        print("\n--- Step 6b: Triggering rekordbox import ---")
        if not trigger_rekordbox_import():
            print("Could not trigger UI import automatically. Please import manually.")
    else:
        print("\n--- Step 6b: Manual import required ---")
        print("In rekordbox: File > Import > Import Playlist from XML")
        print(f"Select: {sync_paths['xml_library_path']}")
    
    print("\n=== FULLY automated workflow complete ===")
    print(f"Backup saved at: {backup_path}")
    
    if not auto_import:
        print("\nFinal step: Import the XML into rekordbox")
        print("File > Import > Import Playlist from XML")
        print(f"Select: {sync_paths['xml_library_path']}")

