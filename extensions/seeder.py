from models.blacklisted_folder import BlackListerFolder
from models.user import User


class Seeder:
    @staticmethod
    def run_seeds():
        User.seeds()
        BlackListerFolder.seeds()
