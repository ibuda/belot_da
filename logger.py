import os
import logging
import logging.config

PROJ_FOLDER = os.path.dirname(os.path.abspath(__file__))


def logger(name):
    log_path = f'{PROJ_FOLDER}/logger.conf'
    logging.config.fileConfig(log_path)

    return logging.getLogger(name)
