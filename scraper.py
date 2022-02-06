import requests
from bs4 import BeautifulSoup
import re
import json
import pymongo
import boto3
import botocore
from dotenv import load_dotenv
import os
import time

def scrape(event, context):
    load_dotenv()
    s3 = boto3.resource('s3')
    # sets up MongoDb connection & S3
    client = pymongo.MongoClient(os.environ.get("DB_URL"))
    db = client[os.environ.get("DB_NAME")]
    coll = db[os.environ.get("COLL_NAME")]


    #get tickers
    response = requests.get('https://www.jamstockex.com/trading/instruments/?instrument=138sl-jmd')
    ticker_soup = BeautifulSoup(response.content, "html.parser")

    tickers = []
    options = ticker_soup.find_all("option")
    last_updated = 0

    for k,v in coll.find_one({"name": "meta"},{"_id":0, "last_updated": 1}).items():
        last_updated = int(v)

    coll.update_many({"name": "meta"}, {"$unset": {"companies": ""}})

    #append tickers into list
    for tick in options:
        tickers.append(tick['value'])
        # adds company list to mongodb.
        coll.update_one({"name": "meta"}, {"$push":  {"companies":{tick['value'].split("-")[0].upper(): tick.text}}} )    

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
        for price, volume in zip(ohlc_data, volume_data):
            price.append(volume[1])
            ohlcv.append(price)
        return ohlcv


    for comp in tickers:
        ohlcv_data = scape_data(comp)
        comp_tick = comp.split("-")[0].upper()
        print(comp_tick)
        
        # #updates mongoDB with new data
        for ohlcv in ohlcv_data:
            if ohlcv[0] > last_updated:
                update = coll.update_one({"ticker": comp_tick}, {"$push":  {"ohlcv":  ohlcv}})
                print(update)

        for data in coll.find({"ticker": comp_tick}):
            s3object = s3.Object(os.environ.get("S3_BUCKET"), f'jsonv2/{comp_tick}.json')
            s3object.put( Body=(bytes(json.dumps(data["ohlcv"]).encode('UTF-8'))), ContentType='application/json')

    coll.update_one({"name": "meta"}, {"$set": {"Last_update": int(time.time())*1000}})
