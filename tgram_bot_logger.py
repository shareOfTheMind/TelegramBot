import logging
import os

from logging import Logger
from datetime import datetime, timedelta

# Script-level variables
log_directory = '/var/log/tgram_bot_logging'
log_file = os.path.join(log_directory, f'{datetime.now().strftime("%y-%m-%d_%T")}.log')
log_retention_days = 30
current_logger: Logger = None




def setup_logger(level=logging.INFO, log_format=f'[%(levelname)s] %(asctime)s : %(name)s - %(message)s', name='Bot Runner Logger'):
    '''
        #### Set up global logger preferences
        > The global logger will print logging to console and to a file
    '''
    global current_logger

    try:
        
        # Create a custom logger
        logger = logging.getLogger(name)
        logger.setLevel(level)
        


        # Create formatters and add them to handlers (CONSOLE LOGGER)
        formatter = logging.Formatter(fmt=log_format, datefmt='%Y-%m-%d-%H-%M-%S')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)


        try:
            # Create handlers (FILE LOGGER)
            # Create log directory if it doesn't exist
            os.makedirs(log_directory, exist_ok=True)
            os.chmod(log_directory, 0o755)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            print("Failed to create file logger. Could have been directory or set permissions.")


        current_logger = logger
    except Exception as ex:
        print(f"An error occurred while setting up the logger:\n '{ex}'")




def write_log(level: str, message: str):
    '''
        #### Write to the tgram bot logfile
        > Log messages at different levels: 
        > - `'info'`
        > - `'warning'` 
        > - `'error'`
        > - `'debug'`
        >
        > Writes logging to both console and file
    '''

    try:
        if level == 'info':
            current_logger.info(message)
        elif level == 'warning':
            current_logger.warning(message)
        elif level == 'error':
            current_logger.error(message)
        else:
            current_logger.debug(message)
    except AttributeError:
        # this will hit if the logger wasn't setup appropiately; for now, we ignore it as this error will be hit when the development environment isn't accounted for within the creation of the logging directory within the setup()
        pass




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
