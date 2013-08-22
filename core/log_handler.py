from __future__ import print_function

import logging


def configure_logging(verbose=False):
    logging.getLogger('boto').setLevel(logging.CRITICAL)
    logging.getLogger("requests").setLevel(logging.CRITICAL)
        
    console = ColorLog()
    console.setLevel(logging.DEBUG if verbose else logging.INFO)
    logging.getLogger('').addHandler(console)
    logging.getLogger('').setLevel(logging.DEBUG)


def _wrap_with(code):

    def inner(text, bold=False):
        c = code
        if bold:
            c = "1;%s" % c
        return "\033[%sm%s\033[0m" % (c, text)
    return inner

red = _wrap_with('31')
green = _wrap_with('32')
yellow = _wrap_with('33')
blue = _wrap_with('34')
magenta = _wrap_with('35')
cyan = _wrap_with('36')
white = _wrap_with('37')


class ColorLog(logging.Handler):
    """
    A class to print colored messages to stdout
    """

    COLORS = {
                logging.CRITICAL: red,
                logging.ERROR: red,
                logging.WARNING: yellow,
                logging.INFO: green,
                logging.DEBUG: lambda x: x,
              }
    
    def __init__(self):
        logging.Handler.__init__(self)

    def usesTime(self):
        return False

    def emit(self, record):
        color = self.COLORS.get(record.levelno, lambda x: x)
        print(color(record.msg))
        