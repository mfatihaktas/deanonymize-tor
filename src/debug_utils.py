import inspect
import logging
import os
import pprint
import sys


# Ref:
# - https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
# - https://github.com/herzog0/best_python_logger
class CustomFormatter(logging.Formatter):
    grey = "\x1b[0;37m"
    green = "\x1b[1;32m"
    yellow = "\x1b[1;33m"
    red = "\x1b[1;31m"
    purple = "\x1b[1;35m"
    blue = "\x1b[1;34m"
    light_blue = "\x1b[1;36m"
    reset = "\x1b[0m"
    blink_red = "\x1b[5m\x1b[1;31m"
    # format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    format = "%(levelname)s] %(file_name)s:%(line_number)s-%(func_name)s: %(message)s"

    FORMATS = {
        logging.DEBUG: reset + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: blink_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  Log  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# LOGGING_FORMAT = "%(levelname)s] %(func_name)s: %(msg)s"
LOGGING_FORMAT = "%(levelname)s] %(file_name)s:%(line_number)s-%(func_name)s: %(message)s"
# LOGGING_FORMAT = "%(levelname)s:%(filename)s:%(lineno)s-%(funcName)s: %(message)s"

# formatter = logging.Formatter(LOGGING_FORMAT)
formatter = CustomFormatter()

LOGGER_NAME = "serv_rate"
# logging.basicConfig(level=logging.INFO) #, format=LOGGING_FORMAT)
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.DEBUG)

def log_to_std():
    logger = logging.getLogger(LOGGER_NAME)
    # TODO: Not sure why this was needed to silence the
    # annoying duplicate logging.
    logger.handlers.clear()

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

log_to_std()

DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3
CRITICAL = 4

level_log_m = {
    INFO: logger.info,
    DEBUG: logger.debug,
    WARNING: logger.warning,
    ERROR: logger.error,
    CRITICAL: logger.critical,
}


def log_to_file(filename, directory=None):
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    logger = logging.getLogger(LOGGER_NAME)

    filepath = "{}/{}".format(directory, filename)
    fh = logging.FileHandler(filepath, mode="w")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def get_extra():
    # frame = inspect.currentframe().f_back.f_back.f_code
    callerframerecord = inspect.stack()[2]  # 0: this line, 1: line at caller
    frame = callerframerecord[0]
    frame_info = inspect.getframeinfo(frame)
    return {
        # "func_name": "{}::{}".format(os.path.split(frame.co_filename)[1], frame.co_name)
        "file_name": os.path.split(frame_info.filename)[1],
        "func_name": frame_info.function,
        "line_number": frame_info.lineno,
    }


def log(level: int, _msg_: str, **kwargs):
    level_log_m[level](f"{_msg_}{pstr(**kwargs)}", extra=get_extra())


## Always log
def alog(level: int, _msg_: str, **kwargs):
    logger.critical("{}\n{}".format(_msg_, pstr(**kwargs)), extra=get_extra())


def pstr(**kwargs):
    if len(kwargs) == 0:
        return ""
    else:
        s = "\n"
        for k, v in kwargs.items():
            s += f"  {k}: {pprint.pformat(v)}\n"
        return s


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  Sim log  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def slog(level: int, env, caller: str, _msg_: str, **kwargs):
        level_log_m[level]("t: {:.2f}] {}: {} {}".format(env.now, caller, _msg_, pstr(**kwargs)), extra=get_extra())


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  Assert  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def check(condition: bool, _msg_: str, **kwargs):
    if not condition:
        logger.error("{}\n{}".format(_msg_, pstr(**kwargs)), extra=get_extra())
        raise AssertionError()


def assert_(_msg_: str, **kwargs):
    logger.error("{}\n{}".format(_msg_, pstr(**kwargs)), extra=get_extra())
    raise AssertionError()
