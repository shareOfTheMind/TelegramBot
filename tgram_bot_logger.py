import logging
import os

from logging import Logger
from datetime import datetime, timedelta

# Script-level variables
log_directory = '/var/log/tgram_bot_logging'
log_file = os.path.join(log_directory, f'{datetime.now().strftime("%y-%m-%d_%T")}.log')
log_retention_days = 30
current_logger: Logger = None




def setup_logger(level=logging.INFO, log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
    global current_logger

    os.makedirs(log_directory, exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    current_logger = logging.getLogger(__name__)
    return current_logger


def write_log(level: str, message: str, logger: Logger=current_logger):
    if level == 'info':
        logger.info(message)
    elif level == 'warning':
        logger.warning(message)
    elif level == 'error':
        logger.error(message)
    else:
        logger.debug(message)


def remove_old_logs(days=log_retention_days):
    cutoff_date = datetime.now() - timedelta(days=days)
    for root, dirs, files in os.walk(log_directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                file_modified_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_modified_date < cutoff_date:
                    os.remove(file_path)


# Example usage
# if __name__ == '__main__':
#     logger = setup_logger()
#     write_log(logger, 'info', 'Logger configured and ready.')
#     remove_old_logs()
