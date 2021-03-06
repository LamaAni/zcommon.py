import os
import sys
import logging
from typing import List
from enum import Enum

try:
    import colorama

    colorama.init()
except Exception:
    pass


class OS_SIMPLE_TYPES(Enum):
    windows = "windows"
    linux = "linux"
    mac = "mac"
    other = "other"


OS_TYPE: OS_SIMPLE_TYPES = OS_SIMPLE_TYPES.other

if sys.platform == "linux" or sys.platform == "linux2":
    OS_TYPE = OS_SIMPLE_TYPES.linux
elif sys.platform == "darwin":
    OS_TYPE = OS_SIMPLE_TYPES.mac
elif sys.platform == "win32":
    OS_TYPE = OS_SIMPLE_TYPES.windows


def get_is_no_color():
    val = os.environ.get("NO_COLOR", "--no-color" in sys.argv)
    if not isinstance(val, bool):
        val = val.strip().lower()
        os.environ["NO_COLOR"] = val
    return val


def colorize(val, color, add_reset=True):
    if get_is_no_color():
        return val
    return color + val + ("\033[0m" if add_reset else "")


class style:
    GRAY = lambda x: colorize(str(x), "\033[90m")  # noqa: E731
    LIGHT_GRAY = lambda x: colorize(str(x), "\033[37m")  # noqa: E731
    BLACK = lambda x: colorize(str(x), "\033[30m")  # noqa: E731
    RED = lambda x: colorize(str(x), "\033[31m")  # noqa: E731
    GREEN = lambda x: colorize(str(x), "\033[32m")  # noqa: E731
    YELLOW = lambda x: colorize(str(x), "\033[33m")  # noqa: E731
    BLUE = lambda x: colorize(str(x), "\033[34m")  # noqa: E731
    MAGENTA = lambda x: colorize(str(x), "\033[35m")  # noqa: E731
    CYAN = lambda x: colorize(str(x), "\033[36m")  # noqa: E731
    WHITE = lambda x: colorize(str(x), "\033[97m")  # noqa: E731
    UNDERLINE = lambda x: colorize(str(x), "\033[4m")  # noqa: E731
    RESET = lambda x: colorize(str(x), "\033[0m")  # noqa: E731


# region Cli text formatter
# -------------------


class CliTableFormatter:
    column_widths: List[str] = None

    def __init__(self):
        super().__init__()
        self.column_widths = []

    def auto_format_columns(self, cols: list):
        col_idx = 0
        formatted = []
        for val in cols:
            str_val = str(val)
            if len(self.column_widths) <= col_idx:
                self.column_widths.append(len(str_val))
            elif len(str_val) > self.column_widths[col_idx]:
                self.column_widths[col_idx] = len(str_val)
            else:
                str_val = str_val.ljust(self.column_widths[col_idx])

            formatted.append(str_val)
            col_idx += 1

        return formatted


# endregion

# region Logger
# -------------------


class ZCommonLogFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    def __init__(self, fmt=None, datefmt=None, style="%"):
        super().__init__(fmt, datefmt, style)
        self.use_colors = "--no-color" not in sys.argv and os.environ.get("NOCOLOR", "").lower().strip() != "true"

    formatter = logging.Formatter("[%(time_marker)s][%(level_marker)s] %(message)s")

    FORMATS = {
        logging.DEBUG: style.GRAY,
        logging.INFO: style.WHITE,
        logging.WARNING: style.YELLOW,
        logging.ERROR: style.RED,
        logging.CRITICAL: style.MAGENTA,
    }

    FORMATTERS = {}

    def format(self, record):
        level_marker: str = record.levelname
        level_marker = level_marker.rjust(8, " ")
        time_marker = self.formatter.formatTime(record)

        if self.use_colors:
            marker_format = self.FORMATS.get(record.levelno)
            level_marker = marker_format(level_marker)
            time_marker = style.GRAY(time_marker)
        else:
            level_marker = level_marker

        record.level_marker = level_marker
        record.time_marker = time_marker

        return self.formatter.format(record)


logger = logging.getLogger("filebase_api")
common_stream_handler = logging.StreamHandler()
common_stream_handler.setFormatter(ZCommonLogFormatter())
logger.addHandler(common_stream_handler)

# endregion
