import os
from typing import List
from models.season import Season
from models.setting import Setting
from extensions.database import db


class ConfigHelper:
    app = None

    @staticmethod
    def custom_logic_for_setting(name, new_value):
        setting = Setting.query.filter_by(name=name).first()
        if not setting:
            return

        old_value = setting.value
        if name == 'SHOW_MAIN_PATH':
            ConfigHelper.redefined_season_paths(old_value, new_value)

    @staticmethod
    def redefined_season_paths(old_dir, new_dir):
        all_seasons: List[Season] = Season.query.all()
        for season in all_seasons:
            path = season.path
            new_path = new_dir + path[len(old_dir):]
            season.path = new_path
        db.session.commit()

    @staticmethod
    def reload_configurations():

        # Settings
        ConfigHelper.app.config['SHOW_MAIN_PATH'] = fr"D:\Vid"
        ConfigHelper.app.config['VLC_MEDIA_PLAYER_EXECUTABLE_PATH'] = fr"C:/Program Files/VideoLAN/VLC/vlc.exe"

        for index, setting in enumerate(ConfigHelper.app.config):
            if index < 34:  # Default configs
                continue
            found_setting = Setting.query.filter_by(name=setting).first()
            if found_setting is None:
                value = ConfigHelper.app.config[setting]
                data_type = type(ConfigHelper.app.config[setting]).__name__
                found_setting = Setting(name=setting, value=str(value), data_type=data_type)
                db.session.add(found_setting)
                db.session.commit()
            else:
                value = found_setting.value
                data_type = found_setting.data_type
                ConfigHelper.app.config[setting] = found_setting.value
