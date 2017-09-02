import os
import logging
from logging.handlers import RotatingFileHandler


ROOTPATH = os.path.dirname(os.path.realpath(__file__))

username = 'HealthyBeautyTrends'
password = 'TechsyleTemporary123'


settings_file_path = os.path.join(ROOTPATH, "settings")


log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
logFile = os.path.join(ROOTPATH, "log")
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5 * 1024 * 1024, backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
logger = logging.getLogger('root')
logger.setLevel(logging.INFO)
logger.addHandler(my_handler)