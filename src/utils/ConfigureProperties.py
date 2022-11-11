import os

from jproperties import Properties


class ConfigureProperties:
    @staticmethod
    def get_properties(properties_file):
        configs = Properties(properties_file)
        with open("./" + properties_file, 'rb') as config_file:
            configs.load(config_file)
        return configs
