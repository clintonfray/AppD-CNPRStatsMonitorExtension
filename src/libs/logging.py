import logging
from logging.handlers import RotatingFileHandler

# create logger
logger = logging.getLogger('simple_logger')

# set logging level
logger.setLevel(logging.DEBUG)

# create rotating file handler and set level to debug
handler = RotatingFileHandler('cnpr_app.log', maxBytes=2000, backupCount=2)
handler.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to rotating file handler
handler.setFormatter(formatter)

# add ch to logger
logger.addHandler(handler)
