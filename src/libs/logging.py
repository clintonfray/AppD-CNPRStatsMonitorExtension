import sys
import logging
from logging.handlers import RotatingFileHandler

# create logger
log = logging.getLogger('simple_logger')

# set logging level
log.setLevel(logging.DEBUG)

# create rotating file handler and set level to debug
handler = RotatingFileHandler('cnpr_app.log', backupCount=2)
handler.setLevel(logging.DEBUG)


# create formatters
simple_formatter = logging.Formatter("%(message)s")
detailed_formatter = logging.Formatter(
    "%(asctime)s %(name)s[%(process)d]: %(levelname)s - %(message)s")

# get a top-level "mypackage" logger,
# set its log level to DEBUG,
# BUT PREVENT IT from propagating messages to the root logger
#
log = logging.getLogger('cnrp_app')
log.setLevel(logging.DEBUG)
log.propagate = 0

# create a console handler
# and set its log level to the command-line option
#
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(getattr(logging, 'INFO'))
console_handler.setFormatter(simple_formatter)

# create a file handler
# and set its log level to DEBUG
#
file_handler = logging.handlers.TimedRotatingFileHandler(
    'cnpr_app.log', 'D', 1, 5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(detailed_formatter)

# create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to rotating file handler
handler.setFormatter(formatter)

# add ch to logger
log.addHandler(console_handler)
log.addHandler(file_handler)
