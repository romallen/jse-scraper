import requests
from bs4 import BeautifulSoup
import re
import json
import pymongo
import boto3
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
    # response = requests.get('https://www.jamstockex.com/trading/instruments/?instrument=138sl-jmd')
    # ticker_soup = BeautifulSoup(response.content, "html.parser")
    # response = requests.get('https://s3.ap-northeast-1.amazonaws.com/romallen.com/json/companies.json')
    # compObj = json.loads(response.content)["companies"]
    # tickers = [(x["ticker"]+ "-"+ x["currency"]).lower() for x in compObj]
    # print(tickers)
    # options = ticker_soup.find_all("option")

    #append tickers into list
    # for tick in options:
    #     tickers.append(tick['value'])
    #     # adds company list to mongodb.
    #     coll.update_one({"name": "meta"}, {"$push":  {"companies":{tick['value'].split("-")[0].upper(): tick.text}}} )    
   
    tickers = ['138sl-jmd', '1834-jmd', 'afs-jmd', 'amg-jmd', 'bil-jmd', 'bpow-jmd', 'brg-jmd', 'cabrokers-jmd', 'cac-jmd', 'car-jmd', 'cbny-jmd', 'ccc-jmd', 'cff-jmd', 'chl-jmd', 'cpfv-jmd', 'cpj-jmd', 'dcove-jmd', 'dtl-jmd', 'ecl-jmd', 'efresh-jmd', 'elite-jmd', 'eply-jmd', 'fesco-jmd', 'firstrockjmd-jmd', 'firstrockusd-usd', 'fosrich-jmd', 'ftna-jmd', 'genac-jmd', 'ghl-jmd', 'gk-jmd', 'gwest-jmd', 'honbun-jmd', 'icreate-jmd', 'indies-jmd', 'isp-jmd', 'jamt-jmd', 'jbg-jmd', 'jetcon-jmd', 'jmmbgl-jmd', 'jp-jmd', 'jse-jmd', 'kex-jmd', 'key-jmd', 'kle-jmd', 'kpreit-jmd', 'kremi-jmd', 'kw-jmd', 'lab-jmd', 'lasd-jmd', 'lasf-jmd', 'lasm-jmd', 'lumber-jmd', 'mailpac-jmd', 'massy-jmd', 'mds-jmd', 'meeg-jmd', 'mil-jmd', 'mje-jmd', 'mpccel-jmd', 'mpccel-usd', 'mtl-jmd', 'mtl-usd', 'ncbfg-jmd', 'pal-jmd', 'pbs-usd', 'pjam-jmd', 'pjx-jmd', 'proven-jmd', 'proven-usd', 'ptl-jmd', 'puls-jmd', 'purity-jmd', 'qwi-jmd', 'rjr-jmd', 'roc-jmd', 'salf-jmd', 'scijmd-jmd', 'scijmd-usd', 'sciusd-usd', 'sci-jmd-jmd', 'selectf-jmd', 'selectmd-jmd', 'sep-jmd', 'sgj-jmd', 'sil-jmd', 'sil-usd', 'sj-jmd', 'sml-jmd', 'sos-jmd', 'spurtree-jmd', 'srfjmd-jmd', 'srfusd-usd', 'sslvc-jmd', 'svl-jmd', 'tjh-jmd', 'tjh-usd', 'tropical-jmd', 'ttech-jmd', 'vmil-jmd', 'wig-jmd', 'wisynco-jmd', 'xfund-jmd']
    last_updated = 0

    for k,v in coll.find_one({"name": "meta"},{"_id":0, "last_updated": 1}).items():
        last_updated = int(v)

    coll.update_many({"name": "meta"}, {"$set": {"companies": tickers}})

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

    coll.update_one({"name": "meta"}, {"$set": {"last_update": int(time.time())*1000}})
    

# scrape("event", "context")