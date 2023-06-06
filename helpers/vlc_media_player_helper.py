import subprocess
from typing import List
from xml.dom import minidom
from models.episode import Episode
import urllib.parse
import glob
import os


class VLCMediaPlayerHelper:
    app = None

    @staticmethod
    def generate_xml_playlist_for_show(file_path, episodes: List[Episode], playlist_title='Playlist'):
        root = minidom.Document()

        playlist = root.createElement('playlist')
        playlist.setAttribute('version', "1")
        root.appendChild(playlist)

        playlist_title_el = root.createElement('title')
        playlist_title_el.appendChild(root.createTextNode(playlist_title))
        playlist.appendChild(playlist_title_el)

        tracklist = root.createElement('trackList')
        playlist.appendChild(tracklist)

        playlist_extension = root.createElement('extension')
        playlist_extension.setAttribute('application', 'http://www.videolan.org/vlc/playlist/0')
        playlist.appendChild(playlist_extension)

        # Add tracks to playlist
        for index, episode in enumerate(episodes):
            # Add index to playlist extension
            vlc_item = root.createElement('vlc:item')
            vlc_item.setAttribute('tid', str(index))
            playlist_extension.appendChild(vlc_item)

            track = root.createElement('track')
            tracklist.appendChild(track)

            location = root.createElement('location')

            # Create a url formatted location path
            true_path = os.path.splitdrive(file_path)[0]
            path_without_drive = file_path.split(':', 1)[1]

            joined_path = os.path.join(path_without_drive, episode['filename'])
            path_segments = os.path.normpath(joined_path).split(os.path.sep)
            for index2, segment in enumerate(path_segments):
                true_path += urllib.parse.quote(segment)
                if index2 < len(path_segments) - 1:
                    true_path += "/"

            location.appendChild(root.createTextNode('file:///' + true_path))
            track.appendChild(location)

            episode_title = root.createElement('title')
            episode_title.appendChild(root.createTextNode(urllib.parse.quote(episode['title'])))
            track.appendChild(episode_title)

            episode_extension = root.createElement('extension')
            episode_extension.setAttribute('application', "http://www.videolan.org/vlc/playlist/0")
            track.appendChild(episode_extension)

            episode_id = root.createElement('vlc:id')
            episode_id.appendChild(root.createTextNode(str(index)))
            episode_extension.appendChild(episode_id)

        xml_str = root.toprettyxml(indent="\t")

        with open(os.path.join(file_path, playlist_title + '.xspf'), "w+") as f:
            xml_str = xml_str.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8" ?>', 1)
            f.write(xml_str)

    @staticmethod
    def show_has_playlist(show_path):
        extension = "xspf"
        return len(glob.glob(show_path + '/*.'+extension)) > 0

    @staticmethod
    def open_file(path: str):
        if not os.path.exists(path):
            return False

        # VLC executable path
        vlc_executable = VLCMediaPlayerHelper.app.config['VLC_MEDIA_PLAYER_EXECUTABLE_PATH']

        # Open the file with VLC
        subprocess.run([vlc_executable, path])

        return True

    @staticmethod
    def open_playlist(path: str):
        if not os.path.exists(path):
            return False

        for filename in os.listdir(path):
            if filename.endswith('.xspf'):
                file_path = os.path.join(path, filename)
                # VLC executable path
                vlc_executable = VLCMediaPlayerHelper.app.config['VLC_MEDIA_PLAYER_EXECUTABLE_PATH']

                # Open the file with VLC
                subprocess.run([vlc_executable, '--playlist-enqueue', file_path])
                return True

        return False
