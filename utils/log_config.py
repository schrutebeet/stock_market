from pathlib import Path
import logging 
import logs
import os
from datetime import datetime

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_path = os.environ.get('LOGS_PATH')

# Create a file handler and set level to INFO
current_datetime = datetime.now()
log_file = os.path.join(log_path, f'{current_datetime.strftime("%Y_%m_%d__%H_%M_%S")}.txt')
if not os.path.exists(log_file):
    with open(log_file, 'w') as file:
        file.write(f"Stock log with timestamp {current_datetime}.\n")

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Create a console handler and set level to INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter and set it for both handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def add_separator():
    separator = '-' * 40  # Customize the separator line as you like
    logging.info(separator)