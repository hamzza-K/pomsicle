import os
import sys
import configparser
from configparser import SectionProxy


def config(translator: str = 'pomsicle') -> SectionProxy:
    """Returns the project credentials/configurations"""
    
    base_path = os.path.dirname(__file__)
    if getattr(sys, 'frozen', False):  # Check if running as an executable (.exe)
        pass # TODO: Handle frozen executable case

    config = configparser.ConfigParser()
    config_file = os.path.join(base_path, 'config/config.cfg')
    config.read(config_file)
    settings = config[translator]

    return settings
