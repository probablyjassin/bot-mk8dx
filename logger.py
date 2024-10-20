import logging
import colorlog

def setup_logger(name):
    """Set up a logger with colorlog and file handler."""
    # Stream handler for console output with color
    stream_handler = colorlog.StreamHandler()
    stream_handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    ))

    # File handler for logging to a file
    file_handler = logging.FileHandler('discord.log')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    logger = logging.getLogger(name)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    return logger

def highlight(text):
    """Highlight in magenta."""
    return f'\033[95m{text}\033[0m'

def normal(text):
    """White text."""
    return f'\033[97m{text}\033[0m'