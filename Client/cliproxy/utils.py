import optparse
import sys
import signal
from logger import *


def get_options():
    levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    usage = "python %prog [options]"
    parser = optparse.OptionParser(usage=usage, description=__doc__)
    parser.add_option("-p", "--port",
                      dest="port",
                      metavar="PORT",
                      type="int",
                      default=80,
                      help="local TCP port [default: %default]")
    parser.add_option("-l", "--level",
                      dest="level",
                      metavar="LEVEL",
                      choices=levels,
                      default=levels[0],
                      help="logging level: " + ", ".join(levels) + " [default: %default]")
    parser.add_option("-q", "--quiet",
                      dest="quiet",
                      default=False,
                      action="store_true",
                      help="suppress console output")
    options, args = parser.parse_args()
    return options


def install_signal_handlers():
    def signal_term_handler(signal, frame):
        logger.critical("terminated by SIGTERM")
        sys.exit(1)

    signal.signal(signal.SIGTERM, signal_term_handler)
