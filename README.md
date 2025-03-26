# Stock Data Scraping and Storage :chart_with_upwards_trend:

This project automates the extraction of stock data from an API, processes the data, and stores it in a database. It handles both daily and minute-level stock data, performs necessary transformations, and sends a notification upon successful execution. The core of the application is written in Python, and it integrates with a database to store the stock information.

## Features

- **Stock Data Extraction**: Fetches metadata and stock data (OHLCV) for different stocks.
- **Data Storage**: Stores the data in a database (supports daily and minute-level data).
- **Email Notification**: Sends a success notification after the process is complete.
- **Logging**: Comprehensive logging of the process, including both info and debug-level logs.

## Requirements

Before running this project, ensure you have the following dependencies installed:

- Python 3.x
- Required Python packages (listed in `requirements.txt`)

## Installation

### Clone the repository

```bash
git clone <repository_url>
cd <repository_directory>
