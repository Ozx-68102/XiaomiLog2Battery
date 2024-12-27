import json
import logging
import logging.handlers
import multiprocessing
import os

from Modules.LogRecord import ColorHandler


class StreamHandler(logging.StreamHandler):
    def __init__(self, color_map: dict[int, str]):
        super().__init__()
        self.ch = ColorHandler()
        self.color_map = color_map

    def emit(self, record):
        msg = self.format(record)

        if record.levelno in self.color_map:
            msg = self.ch.color(msg=msg, color=self.color_map[record.levelno])

        self.stream.write(msg + self.terminator)
        self.flush()


class BaseLog:
    def __init__(self, filename: str) -> None:
        # Read data from json
        config = self.load_config()
        file_config = config["file_handler"]
        logger_path = os.path.abspath(file_config["path"])
        os.makedirs(logger_path, exist_ok=True)

        path = os.path.join(logger_path, filename)

        stream_handler_config = config["stream_handler"]
        self.stream_level = stream_handler_config["level"]
        self.stream_fmt = stream_handler_config["formatter"]["fmt"]

        # translate it by using Dictionary Comprehensions and don't need to modify the JSON file
        self.color_map = {getattr(logging, key): value for key, value in config["color_map"].items()}

        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt=file_config["formatter"]["fmt"], datefmt=file_config["formatter"]["datefmt"])

        file_handler = logging.handlers.RotatingFileHandler(path, maxBytes=file_config["maxBytes"],
                                                            backupCount=file_config["backupCount"])
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, file_config["level"]))
        self.logger.addHandler(file_handler)

    @staticmethod
    def load_config() -> dict:
        filepath = os.path.join(os.path.dirname(__file__), "LoggerConfig.json")
        with open(file=filepath, mode="r") as config_file:
            return json.load(config_file)

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


class Log(BaseLog):
    """ For single-process environments """
    def __init__(self, filename: str):
        super().__init__(filename)

        stream_formatter = logging.Formatter(fmt=self.stream_fmt)
        stream_handler = StreamHandler(self.color_map)
        stream_handler.setFormatter(stream_formatter)
        stream_handler.setLevel(getattr(logging, self.stream_level))
        self.logger.addHandler(stream_handler)


class LogForMultiProc(BaseLog):
    """ For multiprocess environments """

    def __init__(self, filename: str) -> None:
        super().__init__(filename)

        if multiprocessing.get_start_method() in ("spawn", "forkserver", "fork"):
            # This handler is used to output on stream
            self.queue = multiprocessing.Queue(-1)
            queue_handler = logging.handlers.QueueHandler(self.queue)
            queue_handler.setFormatter(logging.Formatter(fmt=self.stream_fmt))
            queue_handler.setLevel(getattr(logging, self.stream_level))
            self.logger.addHandler(queue_handler)

            self.listener = logging.handlers.QueueListener(self.queue, StreamHandler(self.color_map))
            self.listener.start()

        else:
            err_msg = ("LogForFastComp is designed for multi-process environments only. "
                       "For single-process environments, use the 'Log' class instead.")
            raise RuntimeError(err_msg)

    def stop(self):
        """ Stop the listener in multiprocess """
        if hasattr(self, "listener"):
            self.listener.stop()


if __name__ == '__main__':
    pass