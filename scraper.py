import requests
from bs4 import BeautifulSoup
import re
import json


response = requests.get('https://www.jamstockex.com/trading/instruments/?instrument=138sl-jmd')

ticker_soup = BeautifulSoup(response.content, "html.parser")

tickers = []
options = ticker_soup.find_all("option")

for tick in options:
    tickers.append(tick['value'])
   
t = 'wisynco-jmd'
tick_response = requests.get(f'https://www.jamstockex.com/trading/instruments/?instrument={t}')
company_soup = BeautifulSoup(tick_response.content, "html.parser")
company_data = company_soup.findAll('script')[15].text.strip()
pattern = re.compile(r'data:(.*?),$', re.MULTILINE | re.DOTALL)


ohlc_data = json.loads(pattern.findall(company_data)[5])
volume_data = json.loads(pattern.findall(company_data)[6])
print(volume_data[0])



