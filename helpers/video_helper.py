from threading import Thread
from typing import Dict
from flask import app
import requests
import zipfile
import os
import shutil
import ffmpeg
import subprocess
import platform

from helpers.general_helper import GeneralHelper


class VideoHelper:
    app = None

    conversion_threads: dict = {}

    @staticmethod
    def get_audios_from_video(video_file: str) -> list:
        probe = ffmpeg.probe(video_file)
        audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']

        audios: list = []

        # Extract all audio streams
        for idx, audio in enumerate(audio_streams):
            audios.append({
                "index": audio["index"],
                "language": audio["tags"]["language"],
                "title": audio["tags"]["title"],
            })

        return audios

    @staticmethod
    def get_subtitles_from_video(video_file: str) -> list:
        probe = ffmpeg.probe(video_file)
        subtitle_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'subtitle']

        subtitles: list = []

        # Extract all subtitles
        for idx, subtitle in enumerate(subtitle_streams):
            subtitles.append({
                "index": subtitle["index"],
                "language": subtitle["tags"]["language"],
                "title": subtitle["tags"]["title"],
            })

        return subtitles

    @staticmethod
    def convert_video_to_hls(input_video: str, segment_directory: str, segment_filename: str, segment_duration: int, preset: str = "veryfast") -> None:
        # Create output directory if it doesn't exist
        os.makedirs(segment_directory, exist_ok=True)

        probe = ffmpeg.probe(input_video)
        duration: int = probe['format']['duration']

        # Create silent audio
        subprocess.run(
            f'ffmpeg -f lavfi -i anullsrc=r=48000:cl=stereo -t {duration} -c:a aac -b:a 32k -y {segment_directory}/silent.aac',
        )

        # Get subtitles
        subtitles: list = VideoHelper.get_subtitles_from_video(input_video)

        # Convert subtitles into segments
        for index in range(len(subtitles)):
            subprocess.run(
                f'ffmpeg -y -i {input_video} -map 0:s:{index} -c:s webvtt -muxdelay 0 {segment_directory}/{segment_filename}_subtitles_{index}.vtt',
                shell=True
            )

            subprocess.run(
                f'ffmpeg -y -i {segment_directory}/silent.aac -i {segment_directory}/{segment_filename}_subtitles_{index}.vtt -map 0:a:0 -c:v copy -map 1:s:0 -c:s webvtt -f hls -hls_time {segment_duration} -hls_playlist_type vod -muxdelay 0 {segment_directory}/{segment_filename}_subtitles_{index}.m3u8',
                shell=True
            )

            # Delete temporary files
            os.remove(f"{segment_directory}/{segment_filename}_subtitles_{index}.m3u8")

        # Delete empty subtitle video files and keep only subtitles themselves
        for file in os.listdir(segment_directory):
            if file.startswith(f"{segment_filename}_subtitles_") and file.endswith(".ts"):
                os.remove(os.path.join(segment_directory, file))
        os.remove(f"{segment_directory}/silent.aac")

        audios: list = VideoHelper.get_audios_from_video(input_video)

        # Convert audios into segments
        for index in range(len(audios)):
            subprocess.run(
                f'ffmpeg -y -i {input_video} -map 0:a:{index} -c:a aac -strict -2 -muxdelay 0 {segment_directory}/{segment_filename}_audio_{index}.aac',
                shell=True
            )
            subprocess.run(
                f'ffmpeg -i {segment_directory}/{segment_filename}_audio_{index}.aac -c:a copy -f hls -hls_time {segment_duration} -hls_playlist_type vod -muxdelay 0 {segment_directory}/{segment_filename}_audio_{index}.m3u8',
                shell=True
            )

            # Delete temporary files
            os.remove(f"{segment_directory}/{segment_filename}_audio_{index}.aac")

        # Convert video into segments
        subprocess.run(
            f'ffmpeg -y -i {input_video} -map 0:v:0 -c:v libx264 -pix_fmt yuv420p -crf 20 -preset {preset} -hls_time {segment_duration} -hls_playlist_type vod -hls_segment_filename {segment_directory}/{segment_filename}_video_%03d.ts -muxdelay 0 {segment_directory}/{segment_filename}_video.m3u8',
            shell=True
        )

        # Create a master playlist
        with open(f"{segment_directory}/{segment_filename}.m3u8", "w") as f:
            f.write("#EXTM3U\n")
            f.write("#EXT-X-VERSION:3\n")

            japanese_keywords: list = ["jpn", "jp", "japanese", "japan", "jap"]

            # Write audios
            for index, audio in enumerate(audios):
                language: str = audio["language"]
                title: str = audio["title"]
                name: str = f"{language}"
                if title != "":
                    name = f"{title} ({language})"
                f.write(f'#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio",NAME="{name}",DEFAULT={"YES" if language in japanese_keywords else "NO"},AUTOSELECT=YES,LANGUAGE="{language}",URI="{segment_filename}_audio_{index}.m3u8"\n')

            # Write subtitles
            for index, subtitle in enumerate(subtitles):
                language: str = subtitle["language"]
                title: str = subtitle["title"]
                name: str = f"{language}"
                if title != "":
                    name = f"{title} ({language})"
                f.write(f'#EXT-X-MEDIA:TYPE=SUBTITLES,GROUP-ID="subs",NAME="{name}",DEFAULT={"YES" if language in japanese_keywords else "NO"},AUTOSELECT=YES,LANGUAGE="{language}",URI="{segment_filename}_subtitles_{index}_vtt.m3u8"\n')

            f.write("\n")
            f.write('#EXT-X-STREAM-INF:BANDWIDTH=800000,AVERAGE-BANDWIDTH=600000,CODECS="avc1.42c00d,mp4a.40.2",AUDIO="audio",SUBTITLES="subs"\n')
            f.write(f"{segment_directory}_video.m3u8\n")

            VideoHelper.conversion_threads.pop(input_video)

    @staticmethod
    def create_video_segment_thread(input_video: str, segment_directory: str, segment_filename: str, segment_duration: int, preset: str = "veryfast") -> None:
        if not VideoHelper.is_ffmpeg_installed():
            return

        # If video is already being converted
        if input_video in VideoHelper.conversion_threads:
            return

        # Create a conversion thread that converts the video
        thread: Thread = Thread(target=lambda: VideoHelper.create_video_segment_thread(input_video, segment_directory, segment_filename, segment_duration, preset))
        VideoHelper.conversion_threads[input_video] = thread
        thread.start()

    @staticmethod
    def install_ffmpeg() -> bool:
        download_url: str = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        response = requests.get(download_url)

        zip_file_path: str = f"{VideoHelper.app.config['FFMPEG_PATH']}.7z"

        # Save the zip file
        with open(zip_file_path, 'wb') as f:
            f.write(response.content)

        # Extract the contents of the zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(VideoHelper.app.config["FFMPEG_PATH"])

        # Iterate through all directories and move files to the parent directory
        for root, dirs, files in os.walk(VideoHelper.app.config["FFMPEG_PATH"]):
            for file in files:
                source_path = os.path.join(root, file)
                destination_path = os.path.join(VideoHelper.app.config["FFMPEG_PATH"], file)
                shutil.move(source_path, destination_path)

        # Remove the now empty directories
        for root, dirs, files in os.walk(VideoHelper.app.config["FFMPEG_PATH"], topdown=False):
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))

        # Get the PATH separator based on the OS
        path_separator = ';' if platform.system() == 'Windows' else ':'

        # Check if folder path already exists in PATH
        paths = os.environ['PATH'].split(path_separator)
        if VideoHelper.app.config["FFMPEG_PATH"] not in paths:
            # Append the folder path to PATH
            os.environ['PATH'] += path_separator + VideoHelper.app.config["FFMPEG_PATH"]

            # Optionally, you can also save the new PATH for the current session
            if platform.system() == 'Windows':
                os.system(f'setx PATH "%PATH%"')
            else:
                os.system(f'export PATH="$PATH"')

        return VideoHelper.is_ffmpeg_installed() and response.ok

    @staticmethod
    def get_ffmpeg_executable_path() -> str:
        return os.path.join(VideoHelper.app.config["FFMPEG_PATH"], "ffmpeg.exe")

    @staticmethod
    def is_ffmpeg_installed() -> bool:
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def get_running_conversion() -> list:
        return VideoHelper.conversion_threads.keys()

    @staticmethod
    def is_video_converting(video_path: str) -> bool:
        return video_path in VideoHelper.conversion_threads
