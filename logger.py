import sys
from functools import partial



class Logger(object):
    """Module to handle logging messages to the screen"""

    # escape sequences for changing terminal text color
    SCR_COLORS = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "default": "\033[39m",
    }


    # available log messages; key-string pairs are added in the constructor when
    # the logger's constructor is called with a list of messages; logger error
    # messages can be overridden and customized by providing alternates at
    # initialization time
    _internal_fmt_strings = {
        "err_msg":        "Error [{err_code}]: {err_msg}",
        "err_no_fmt_str": "Could not find format string with key '{fmt_key}'",
        "err_fmt_no_key": "Missing value for format argument '{fmt_arg}' in format string '{bad_key}'",
        "err_bad_color":  "Color '{color}' not valid",
    }


    def __init__(self, fmt_strings={}, enabled=True, use_colors=True):
        """Initialize the logger and its collection of messages"""

        self._enabled = enabled
        self._use_colors = use_colors

        # start with internal format strings, then merge in the provided
        # strings, overwriting default internal strings
        self._fmt_strings = Logger._internal_fmt_strings.copy()
        self._fmt_strings.update(fmt_strings)

        # provide aliases to for common logging operations
        self.success = partial(self.log, color="green")
        self.info    = partial(self.log, color="cyan")
        self.warning = partial(self.log, color="yellow")
        self.error   = partial(self.log, color="red")


    # utility methods to enable/disable the logger
    def enable(self):
        self._enabled = True
    def disable(self):
        self._enabled = False

    # utility methods to enable/disable colors (such as when logging to a file)
    def enable_color(self):
        self._use_colors = True
    def disable_color(self):
        self._use_colors = False


    def log(self, msg, color=None, **kwargs):
        """Log a message, injecting format arguments and setting text color"""

        if self._enabled:
            if kwargs:
                # if format arguments were provided, populate the message string
                # with those values
                msg = self._format(msg, **kwargs)

            if color and self._use_colors:
                # set the text color if specified and enabled
                msg = self._color(msg, color)

            # print the final result
            return self._do_log(msg)


    def _do_log(self, msg):
        """Perform the actual log operation (may be overridden)"""

        print(msg)


    def _internal_error(self, err_code, **kwargs):
        """Log an internal error within the logger itself"""

        # add prefix and contribute the err_code to the format arguments
        err_msg = self._format(err_code, err_code=err_code, **kwargs)
        return self.error("err_msg", err_code=err_code, err_msg=err_msg)

    def _format(self, fmt_key, **kwargs):
        """Injects values into a format string, handling errors"""

        result = fmt_key

        try: # get the format string for the specified key
            result = fmt_str = self._fmt_strings[fmt_key]

            try: # populate the format string with values
                result = fmt_str.format(**kwargs)
            except KeyError, e:
                # swallow but log the error if a format argument is missing
                self._internal_error("err_fmt_no_key",
                    fmt_arg=e.message, bad_key=fmt_key)
        except KeyError:
            # swallow and log the error if an invalid format string is specified
            self._internal_error("err_no_fmt_str", fmt_key=fmt_key)

        return result


    def _color(self, msg, color=None):
        """Sets the color of a message before logging"""

        try:
            # set color + write message + reset color to default
            msg = Logger.SCR_COLORS[color] + msg + Logger.SCR_COLORS["default"]
        except KeyError:
            # ignore invalid colors
            self._internal_error("err_bad_color", color=color)

        return msg


class FileLogger(Logger):
    """Module to handle logging messages to a file"""

    def __init__(self, outfile, fmt_strings={}, enabled=True):
        """Initialize the logger and its collection of messages"""
        super(FileLogger, self).__init__(fmt_strings, enabled=True, use_colors=False)
        self.logfile = open(outfile, "w")

    def _do_log(self, msg):
        self.logfile.write(msg + "\n")

if __name__ == "__main__":
    logger = Logger({ "test_fmt_str": "{arg}" })

    logger.log("Simple message") # basic log
    logger.log("test_fmt_str", arg="test") # basic substitution
    logger.log("test_fmt_str", arg="test", arg2="test2") # extra args

    # test color variants
    logger.success("test_fmt_str", arg="test")
    logger.info("test_fmt_str", arg="test")
    logger.warning("test_fmt_str", arg="test")
    logger.error("test_fmt_str", arg="test")

