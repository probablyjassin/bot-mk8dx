import logging
import colorlog


def setup_logger(
    name: str, file: str = "discord.log", file_mode: str = "w", console: bool = True
) -> logging.Logger:
    """Set up a logger with colorlog and file handler."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if console:
        stream_handler = colorlog.StreamHandler()
        stream_handler.setFormatter(
            colorlog.ColoredFormatter(
                "%(log_color)s%(message)s",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            )
        )
        logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(f"logs/{file}", mode=file_mode, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)

    return logger


def highlight(text):
    """Highlight in magenta."""
    return f"\033[95m{text}\033[0m"
