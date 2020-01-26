import sys
import logging
import logging.config


def logger(name):
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        LOGGER.error("Uncaught exception", exc_info=(
            exc_type, exc_value, exc_traceback))

    LOGGER = logging.getLogger(name)
    sys.excepthook = handle_exception

    return logging.getLogger(name)
