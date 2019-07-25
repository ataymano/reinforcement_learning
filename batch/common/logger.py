import logging
import sys

def CreateLogger(level='INFO'):
    logger = logging.getLogger('Logger')
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s]: %(message)s')
    stream_handler.setFormatter(formatter)
    logger.setLevel(logging.getLevelName(level))	#    logger.setLevel(logging.getLevelName(level))
    logger.addHandler(stream_handler)	#    logger.addHandler(stream_handler)
    return logger