import subprocess
import requests
import os
import winreg


class VLCMediaPlayerExtension:
    @staticmethod
    def download():
        url = r"https://get.videolan.org/vlc/3.0.18/win64/vlc-3.0.18-win64.exe"
        response = requests.get(url)
        file = 'vlc_media_player_download.exe'
        with open(file, 'wb+') as f:
            f.write(response.content)

        subprocess.run('./'+file)
        return True

    @staticmethod
    def vlc_media_player_is_downloaded():
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\vlc.exe") as key:
                return True
        except FileNotFoundError:
            return False
