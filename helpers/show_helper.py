import json
import os
from typing import List
from extensions.database import db
from models.blacklisted_folder import BlackListerFolder


class EpisodePath:
    def __init__(self, name: str, file: str) -> None:
        self.name: str = name
        self.file: str = file
        self.suggested_episode_number: int = self._create_suggested_episode_number()

    def _create_suggested_episode_number(self):
        number: int = 0
        name: str = self.file.lower()
        replaced_name = name.replace('.', ' ').replace('-bit', 'temp').replace('-', ' ')
        # Remove version
        for i in range(100):
            replaced_name = replaced_name.replace(f'v{i}', ' ')

        # Remove seasons
        for i in range(1, 100):
            replaced_name = replaced_name.replace(f'season{i}', ' ')
            replaced_name = replaced_name.replace(f'season {i}', ' ')
            replaced_name = replaced_name.replace(f's0{i}e', ' ')
            replaced_name = replaced_name.replace(f's{i}e', ' ')
            replaced_name = replaced_name.replace(f's0{i}', ' ')
            replaced_name = replaced_name.replace(f's0{i}-', ' ')
            replaced_name = replaced_name.replace(f's{i}', ' ')
            replaced_name = replaced_name.replace(f'{i}e', ' ')

        replaced_name = replaced_name.replace('ova', ' ').replace('episode', ' ').replace('ep', ' ').replace('e', ' ').replace("episode", ' ').replace('s00', ' ').replace('_', ' ').replace('.', ' ').replace('-', ' ')

        name_as_list = replaced_name.split(' ')

        for s in name_as_list:
            try:
                i = int(s)
                number = i
                break
            except ValueError as verr:
                pass  # do job to handle: s does not contain anything convertible to int

        return number

    def __repr__(self) -> str:
        return self.toJson()

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class SeasonPath:
    def __init__(self, name, full_path, is_special, episodes: List[EpisodePath]) -> None:
        self.name = name
        self.full_path = full_path
        self.is_special = is_special
        self.episodes = episodes


class SeasonPathEncoder(json.JSONEncoder):
    def default(self, o):
        o_dict = o.__dict__

        # New episodes as __dicts__
        episodes = o_dict['episodes']
        new_episodes = []

        # We need to get the episodes' dict versions too
        for episode in episodes:
            e_dict = episode.__dict__
            new_episodes.append(e_dict)
        o_dict['episodes'] = new_episodes

        return o_dict


class ShowHelper:
    app = None

    def get_path_episodes(path):
        episodes = []
        blacklisted_files = ['.xspf', '.png', '.jpg', '.gif']
        for file in os.listdir(path):
            d = os.path.join(path, file)

            # Name & Folder checks
            if os.path.isdir(d):
                continue

            # Blacklisted file extensions
            filename, file_extension = os.path.splitext(file)
            if (file_extension in blacklisted_files):
                continue

            episode_path = EpisodePath(filename.split(".")[0], file)

            episodes.append(episode_path)
        return episodes

    @staticmethod
    def map_shows_inside_folder(path, all=[], is_inside_episode_folder=False, blacklist=[], is_top_path=False, original_folder=""):
        for file in os.listdir(path):
            d = os.path.join(path, file)

            # Name & Folder checks
            if not os.path.isdir(d):
                continue

            if file in blacklist:
                continue

            full_path: str = os.path.join(path, file)
            if full_path in blacklist:
                continue

            episodes = ShowHelper.get_path_episodes(d)

            # Finds specials & extras too!
            # Is special if there are episodes inside the current folder
            new_all = ShowHelper.map_shows_inside_folder(d, all, len(episodes) > 0, blacklist, False, file)

            # If folder with episodes contains new folders, it is special of this anime
            if len(episodes) > 0:
                name = file
                if original_folder:
                    name = original_folder

                season_path = SeasonPath(name, d, is_inside_episode_folder, episodes)
                new_all.append(season_path)
                all = new_all
        return all

    @staticmethod
    def get_all_show_paths():
        main_folder = ShowHelper.app.config['SHOW_MAIN_PATH']
        blacklisted_folders = [folder.folder_path for folder in BlackListerFolder.query.all()]
        folders = ShowHelper.map_shows_inside_folder(main_folder, [], False, blacklisted_folders, is_top_path=True)
        return folders
