import os
import sys
import configparser


def config(translator: str = 'pomsicle') -> configparser.SectionProxy:
    """Returns the project credentials/configurations"""
    
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    else:
        base_path = os.path.dirname(__file__)

    config = configparser.ConfigParser()
    config_file = os.path.join(base_path, 'config/config.cfg')
    config.read(config_file)

    settings = config[translator]

    return settings
