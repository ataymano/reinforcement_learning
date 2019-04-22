import logging
import sys


def console_logger(node_id, level='INFO'):
    logger = logging.getLogger('dashboard_logger')
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(node_id)s][%(asctime)s]: %(message)s')
    stream_handler.setFormatter(formatter)
    logger.setLevel(logging.getLevelName(level))
    logger.addHandler(stream_handler)
    extra = {'node_id': str(node_id)}
    return logging.LoggerAdapter(logger, extra)
