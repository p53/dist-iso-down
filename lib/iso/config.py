import yaml
import logging
from pattern.singleton import Singleton

class Config(metaclass=Singleton):
    def __init__(self, config_path):
        logger = logging.getLogger('logger')

        try:
            self.config = yaml.load(open(config_path, 'r'))
        except yaml.YAMLError as exc:
            msg = "Error in configuration file: {}".format(exc)
            logger.error(msg)
