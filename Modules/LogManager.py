import logging

from Modules.ColorManager import ColorManager


class StreamHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()
        self.cm = ColorManager()

    def emit(self, record):
        msg = self.format(record)
        color_map = {
            logging.DEBUG: "green",
            logging.INFO: "green",
            logging.WARNING: "yellow",
            logging.ERROR: "red",
            logging.CRITICAL: "red"
        }

        if record.levelno in color_map:
            msg = self.cm.color(msg, color=color_map[record.levelno])

        self.stream.write(msg + self.terminator)
        self.flush()


class Log:
    def __init__(self, path: str, cmd_level: int = logging.INFO, file_level: int = logging.DEBUG) -> None:
        """
        :param path: receive a file path
        :param cmd_level: set stream logging level
        :param file_level: set file logging level
        """
        self.cm = ColorManager()
        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(fmt="[%(asctime)s] [%(levelname)s] %(message)s",
                                           datefmt="%Y-%m-%d %H:%M:%S")
        stream_formatter = logging.Formatter(fmt="[%(levelname)s] %(message)s")

        file_handler = logging.FileHandler(path)
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(file_level)
        self.logger.addHandler(file_handler)

        stream_handler = StreamHandler()
        stream_handler.setFormatter(stream_formatter)
        stream_handler.setLevel(cmd_level)
        self.logger.addHandler(stream_handler)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def warn(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)


if __name__ == '__main__':
    pass
