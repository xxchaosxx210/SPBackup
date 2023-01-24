import logging

# STREAM_LOGGER_NAME = "SPBackupStream"
LOGGER_LEVEL = logging.INFO

def setup_logger() -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(LOGGER_LEVEL)

    # create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOGGER_LEVEL)

    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger