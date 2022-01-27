import requests
from bs4 import BeautifulSoup
import re
import json
import pymongo
from dotenv import load_dotenv
import os


load_dotenv()

# sets up MongoDb connection
client = pymongo.MongoClient(os.environ.get("DB_URL"))
db = client["jse"]
coll = db["companies"]


#get tickers
response = requests.get('https://www.jamstockex.com/trading/instruments/?instrument=138sl-jmd')
ticker_soup = BeautifulSoup(response.content, "html.parser")

tickers = []
options = ticker_soup.find_all("option")

#append tickers into list
for tick in options:
    tickers.append(tick['value'])
    # adds company to mongodb. It only needs to be run once.
    # coll.update_one({"name": "meta"}, {"$push":  {"companies":{tick['value'].split("-")[0].upper(): tick.text}}} )    

def scape_data(company):
    tick_response = requests.get(f'https://www.jamstockex.com/trading/instruments/?instrument={company}')
    company_soup = BeautifulSoup(tick_response.content, "html.parser")
    #get trade data from script tag and strips leading whitespaces
    company_data = company_soup.findAll('script')[15].text.strip()
    pattern = re.compile(r'data:(.*?),$', re.MULTILINE | re.DOTALL)
    #transform data into json objects
    ohlc_data = json.loads(pattern.findall(company_data)[5])
    volume_data = json.loads(pattern.findall(company_data)[6])
    ohlcv = []
    #checks for empty data sets and returns a list with empty values
    if ohlc_data is None:
        return [[0,0,0,0,0,0]]
    #merge ohlc and volume data into one list
    for i in range(len(ohlc_data)):
        price = ohlc_data[i]
        vol = volume_data[i]
        price.append(vol[1])
        ohlcv.append(price)
    return ohlcv


for comp in tickers:
    ohlcv_data = scape_data(comp)
    comp_tick = comp.split("-")[0].upper()
    print(comp_tick)
    #adds entry into MongoDb if it doesn't already exists
    if coll.find({"ticker": comp_tick}).count() == 0:
        coll.insert({"name": comp_tick, "ticker": comp_tick,"blurb" : "Preference Shares/bond", "ohlcv": [[0,0,0,0,0,0]] })
    mongo_data = []
    for data in coll.find({"ticker": comp_tick}):
       mongo_data = data["ohlcv"][-1][0]
    
    #updates mongoDB with new data
    for i in range(len(ohlcv_data)):
        
        if ohlcv_data[i][0] > mongo_data:
            update = coll.update_one({"ticker": comp_tick}, {"$push":  {"ohlcv":  ohlcv_data[i]}})
            print(update)
            
        
            