import logging.config
import os


def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s | %(levelname)s | '
                '%(name)s | %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': 'INFO',
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'logs/scraper.log',
                'mode': 'a',
                'formatter': 'standard',
                'encoding': 'utf-8',
                'level': 'DEBUG',
            },
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }

    logging.config.dictConfig(config)
