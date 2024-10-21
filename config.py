import os
import configparser


def config(translator: str = 'pomsicle') -> list:
    """Returns the project credentials/configurations"""
    config = configparser.ConfigParser()
    config_file = os.path.join(os.path.dirname(__file__), 'config/config.cfg')
    config.read(config_file)
    settings = config[translator]

    return settings
