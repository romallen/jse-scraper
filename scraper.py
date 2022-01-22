import requests
from bs4 import BeautifulSoup

response = requests.get('https://www.jamstockex.com/trading/instruments/?instrument=138sl-jmd')

ticker_soup = BeautifulSoup(response.content, "html.parser")

tickers = []
#select('#stocks')
options = ticker_soup.find_all("option")

for tick in options:
    tickers.append(tick['value'])
   
   
print(tickers) 