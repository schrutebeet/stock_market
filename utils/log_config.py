from pathlib import Path
import logging
import logs
import os


log_folder = Path(logs.__file__).parent
os.makedirs(log_folder, exist_ok=True)

log_file = os.path.join(log_folder, 'stock_market_logs.txt')

# Configuring the 'logging' file
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,  # Setting types of log: INFO, WARNING, ERROR and CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s'
)
