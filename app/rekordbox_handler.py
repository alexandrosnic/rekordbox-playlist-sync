"""Rekordbox XML manipulation and export of playlists to m3u8 files."""

import xml.etree.ElementTree as ET
from utils.utils import get_sync_paths
import os


def remove_duplicates_per_node(node):
    seen_keys = set()
    tracks_to_remove = []
    
    for track in node.findall('TRACK'):
        key = track.get('Key')
        if key in seen_keys:
            tracks_to_remove.append(track)
        else:
            seen_keys.add(key)
    
    for track in tracks_to_remove:
        node.remove(track)

    # Update the Entries attribute
    node.set('Entries', str(len(node.findall('TRACK'))))

def remove_duplicates():
    """
    Remove duplicate TRACK entries within each rekordbox playlist node based
    on the 'Key' attribute.
    """
    sync_paths = get_sync_paths()
    rekordbox_xml = sync_paths["xml_library_path"]

    tree = ET.parse(rekordbox_xml)
    root = tree.getroot()

    # Iterate over each NODE and remove duplicates
    for playlist in root.find('PLAYLISTS').findall('NODE'):
        for node in playlist.findall('NODE'):
            remove_duplicates_per_node(node)

    tree.write(rekordbox_xml, encoding='UTF-8', xml_declaration=True)

    print('Duplicate tracks removed successfully.')


def create_m3u8_playlists_from_xml():
    """
    Parse the rekordbox XML and create M3U8 playlists for each playlist in the
    'rekordboxPlaylists' node.
    """

    # Define paths
    sync_paths = get_sync_paths()
    rekordbox_xml = sync_paths["xml_library_path"]
    output_folder = sync_paths["rekordbox_custom_playlists_m3u8_dir"]

    # Parse the XML file
    tree = ET.parse(rekordbox_xml)
    root = tree.getroot()

    # Find the rekordboxPlaylists node
    rekordbox_playlists_node = root.find(".//NODE[@Name='rekordboxPlaylists']")

    # rekordbox_playlists_node = None
    # for node in root.findall(".//NODE[@Name='rekordboxPlaylists']"):
    #     rekordbox_playlists_node = node
    #     break

    if rekordbox_playlists_node is None:
        print("rekordboxPlaylists node not found in the XML.")
        return

    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Track ID to location mapping
    track_locations = {}
    for track in root.findall(".//COLLECTION/TRACK"):
        track_id = track.get("TrackID")
        location = track.get("Location")
        location = location.replace("file://localhost", "").replace("%20", " ")
        track_locations[track_id] = location

    # Create M3U8 files for each playlist in rekordboxPlaylists
    for playlist_node in rekordbox_playlists_node.findall("NODE"):
        playlist_name = playlist_node.get("Name")
        m3u8_path = os.path.join(output_folder, f"{playlist_name}.m3u8")

        with open(m3u8_path, "w", encoding="utf-8") as m3u8_file:
            m3u8_file.write("#EXTM3U\n")
            for track in playlist_node.findall("TRACK"):
                track_key = track.get("Key")
                track_location = track_locations.get(track_key)
                if track_location:
                    m3u8_file.write(f"{track_location}\n")

        print(f"Created M3U8 playlist: {m3u8_path}")



