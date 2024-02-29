import random
import string
import os
from typing import List


class GeneralHelper:
    @staticmethod
    def generate_random_string(length: int) -> str:
        letters = string.ascii_lowercase
        folder_name = ''.join(random.choice(letters) for _ in range(length))
        return folder_name

    @staticmethod
    def generate_random_folder_path(length: int, parent_folder_path: str, max_tries: int = 100) -> str:
        random_directory_name: str = GeneralHelper.generate_random_string(length)
        random_directory_path: str = os.path.join(parent_folder_path, random_directory_name)

        tries: int = 0
        while os.path.exists(random_directory_path):
            random_directory_name: str = GeneralHelper.generate_random_string(length)
            random_directory_path = os.path.join(parent_folder_path, random_directory_name)

            tries += 1

            if tries > max_tries:
                return ""

        return random_directory_path

    @staticmethod
    def get_folder_size(folder_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    @staticmethod
    def convert_bytes_to_readable(size_in_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024.0:
                break
            size_in_bytes /= 1024.0
        return "{:.2f} {}".format(size_in_bytes, unit)

    def split_path(path: str) -> List[str]:
        path_list = []

        while True:
            head, tail = os.path.split(path)
            if tail == "":
                path_list.append(head)
                break
            path_list.append(tail)
            path = head

        # Reverse the list to get the correct order
        path_list.reverse()
        return path_list
