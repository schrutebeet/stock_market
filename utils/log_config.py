from pathlib import Path
import logging
import logs
import os
from datetime import datetime


log_path = os.environ.get('LOGS_PATH')

current_datetime = datetime.now()
log_file = os.path.join(log_path, f'{current_datetime.strftime("%Y_%m_%d__%H_%M_%S")}.txt')
if not os.path.exists(log_file):
    with open(log_file, 'w') as file:
        file.write(f"Stock log with timestamp {current_datetime}.\n")

def add_separator():
    separator = '-' * 40  # Customize the separator line as you like
    logging.info(separator)

# Configuring the 'logging' file
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,  # Setting types of log: INFO, WARNING, ERROR and CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s'
)
