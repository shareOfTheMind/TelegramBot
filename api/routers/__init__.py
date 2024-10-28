import sys
import os
from datetime import datetime

# Append the base directory of your project to sys.path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(base_dir)

log_directory = '/var/log/api_logging'
log_file = os.path.join(log_directory, f'{datetime.now().strftime("%y-%m-%d_%T")}.log')
# log_directory = r'C:\Users\gaben\Desktop'
# log_file = os.path.join(log_directory, 'test.log')
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(levelname)s] %(asctime)s : (%(name)s) - %(message)s",
            "datefmt": "%Y-%m-%d-%H-%M-%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": log_file,
            "formatter": "default",
            "level": "INFO",
        }
    },
    "loggers": {
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        }
    }
}
