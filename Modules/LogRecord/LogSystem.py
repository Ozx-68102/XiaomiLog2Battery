import logging
import logging.handlers
import multiprocessing

from Modules.LogRecord import ColorHandler


class StreamHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()
        self.ch = ColorHandler()

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
            msg = self.ch.color(msg, color=color_map[record.levelno])

        self.stream.write(msg + self.terminator)
        self.flush()


class BaseLog:
    def __init__(self, path: str) -> None:
        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt="[%(asctime)s] [%(levelname)s] %(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S")

        file_handler = logging.handlers.RotatingFileHandler(path, maxBytes=5 * 1024 * 1024, backupCount= 5)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

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
    def __init__(self, path: str):
        super().__init__(path)

        stream_formatter = logging.Formatter(fmt="[%(levelname)s] %(message)s")
        stream_handler = StreamHandler()
        stream_handler.setFormatter(stream_formatter)
        stream_handler.setLevel(logging.INFO)
        self.logger.addHandler(stream_handler)


class LogForMultiProc(BaseLog):
    """ For multiprocess environments """

    def __init__(self, path: str) -> None:
        super().__init__(path)

        if multiprocessing.get_start_method() in ("spawn", "forkserver", "fork"):
            # This handler is used to output on stream
            self.queue = multiprocessing.Queue(-1)
            queue_handler = logging.handlers.QueueHandler(self.queue)
            queue_handler.setFormatter(logging.Formatter(fmt="[%(levelname)s] %(message)s"))
            queue_handler.setLevel(logging.INFO)
            self.logger.addHandler(queue_handler)

            self.listener = logging.handlers.QueueListener(self.queue, StreamHandler())
            self.listener.start()

        else:
            err_msg = ("LogForFastComp is designed for multi-process environments only. "
                       "For single-process environments, use the 'Log' class instead.")
            raise RuntimeError(err_msg)

    def stop(self):
        """ Stop the listener in multiprocess """
        if hasattr(self, 'listener'):
            self.listener.stop()


if __name__ == '__main__':
    pass