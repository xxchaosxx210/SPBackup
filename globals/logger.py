import logging

STREAM_LOGGER_NAME = "SPBackupStream"
LOGGER_LEVEL = logging.INFO

def setup_logger() -> logging.Logger:
    logger = logging.getLogger(STREAM_LOGGER_NAME)
    logger.setLevel(LOGGER_LEVEL)

    # create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOGGER_LEVEL)

    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


def console(message: str, level: str):
    logger = logging.getLogger(STREAM_LOGGER_NAME)
    if level == "info":
        logger.info(message)
    elif level == "debug":
        logger.debug(message)
    elif level == "warning":
        logger.warning(message)
    else:
        logger.error(message)