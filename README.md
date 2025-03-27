# Stock Data Scraping and Storage :chart_with_upwards_trend::bar_chart:

This project automates the extraction of stock data from the [AlphaVantage API](https://www.alphavantage.co/) , processes the data, and stores it in a database of your choice. It handles several time-level (minute, daily, weekly...) stock data, performs necessary transformations, and sends a notification when successfully executed. This project has been developed using Python, and it can integrate with any PostgreSQL database (local or remote).

## Project features

- **Stock data extraction**: Fetches metadata and stock data (OHLCV) for different stocks. An Alphavantage API key is needed. Can be requested following this [link](https://www.alphavantage.co/support/#support).
- **Data storage**: Stores the data in a PostgreSQL database.
- **Email notification**: Sends a success notification after the process is complete. E-mail credentials are needed in order to enable this feature.
- **Logging**: Comprehensive logging of the process. Can be useful both for reporting and debugging.

## Requirements

Before running this project, ensure you have the following dependencies installed:

- Python 3.x
- Required Python packages (listed in `requirements.txt`)

## Installation

### Clone the repository

```bash
git clone git@github.com:schrutebeet/stock_market.git
cd stock_market
```

## Additional resources
The project also contains the following files:

- **Dockefile**: A Docker file which can be used to build an image of this project and deploy it anywhere. I personally use this option to deploy the project on a Raspberry Pi 3B.
- **stocks_cronjob.sh**: If using images is an expensive option for deploying, you can also add this file as a Cronjob task to be executed in your computer.


## Planning ahead
The next steps for this project include:

- **Portfolios**: Enable portfolios to be created in the project.
- **Dashboards**: Use Graphana or other open source libraries to build comprehensive dashboards with risk management and price predictions, given an instrument or portfolio. 
- **Tests**: Finish unit tests for the source code and reach minimum a 90% coverage level.
