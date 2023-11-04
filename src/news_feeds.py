import requests
import pprint
from dependencies.authenticator import api_key

url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey={api_key}'
r = requests.get(url)
data = r.json()

pprint.pprint(data)