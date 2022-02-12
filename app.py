from bs4 import BeautifulSoup
import re
import json
import pymongo
import boto3
from dotenv import load_dotenv
import os
import time
from concurrent.futures import ThreadPoolExecutor
import requests


load_dotenv()
s3 = boto3.resource('s3')

client = pymongo.MongoClient(os.environ.get("DB_URL"))
db = client[os.environ.get("DB_NAME")]
coll = db[os.environ.get("COLL_NAME")]


last_updated = 0
for k,v in coll.find_one({"name": "meta"},{"_id":0, "last_updated": 1}).items():
    last_updated = int(v)

tickers = ['138sl-jmd', '1834-jmd', 'afs-jmd', 'amg-jmd', 'bil-jmd', 'bpow-jmd', 'brg-jmd', 'cabrokers-jmd', 'cac-jmd', 'car-jmd', 'cbny-jmd', 'ccc-jmd', 'cff-jmd', 'chl-jmd', 'cpfv-jmd', 'cpj-jmd', 'dcove-jmd', 'dtl-jmd', 'ecl-jmd', 'efresh-jmd', 'elite-jmd', 'eply-jmd', 'fesco-jmd', 'firstrockjmd-jmd', 'firstrockusd-usd', 'fosrich-jmd', 'ftna-jmd', 'genac-jmd', 'ghl-jmd', 'gk-jmd', 'gwest-jmd', 'honbun-jmd', 'icreate-jmd', 'indies-jmd', 'isp-jmd', 'jamt-jmd', 'jbg-jmd', 'jetcon-jmd', 'jmmbgl-jmd', 'jp-jmd', 'jse-jmd', 'kex-jmd', 'key-jmd', 'kle-jmd', 'kpreit-jmd', 'kremi-jmd', 'kw-jmd', 'lab-jmd', 'lasd-jmd', 'lasf-jmd', 'lasm-jmd', 'lumber-jmd', 'mailpac-jmd', 'massy-jmd', 'mds-jmd', 'meeg-jmd', 'mil-jmd', 'mje-jmd', 'mpccel-jmd', 'mpccel-usd', 'mtl-jmd', 'mtl-usd', 'ncbfg-jmd', 'pal-jmd', 'pbs-usd', 'pjam-jmd', 'pjx-jmd', 'proven-jmd', 'proven-usd', 'ptl-jmd', 'puls-jmd', 'purity-jmd', 'qwi-jmd', 'rjr-jmd', 'roc-jmd', 'salf-jmd', 'scijmd-jmd', 'scijmd-usd', 'sciusd-usd', 'sci-jmd-jmd', 'selectf-jmd', 'selectmd-jmd', 'sep-jmd', 'sgj-jmd', 'sil-jmd', 'sil-usd', 'sj-jmd', 'sml-jmd', 'sos-jmd', 'spurtree-jmd', 'srfjmd-jmd', 'srfusd-usd', 'sslvc-jmd', 'svl-jmd', 'tjh-jmd', 'tjh-usd', 'tropical-jmd', 'ttech-jmd', 'vmil-jmd', 'wig-jmd', 'wisynco-jmd', 'xfund-jmd']
coll.update_many({"name": "meta"}, {"$set": {"companies": tickers}})

def store_data(data, comp_tick):
    #updates mongoDB with new data
    for ohlcv in data:
        if ohlcv[0] > last_updated:
            update = coll.update_one({"ticker": comp_tick}, {"$push":  {"ohlcv":  ohlcv}})
            print(update)   
        
    for data in coll.find({"ticker": comp_tick}):
        s3object = s3.Object(os.environ.get("S3_BUCKET"), f'jsonv2/{comp_tick}.json')
        s3object.put( Body=(bytes(json.dumps(data["ohlcv"]).encode('UTF-8'))), ContentType='application/json')
 
            
def parse(page,comp_tick):
    soup=BeautifulSoup(page,'html.parser')
    company_data = soup.findAll('script')[15].text.strip()
    pattern = re.compile(r'data:(.*?),$', re.MULTILINE | re.DOTALL)
    #transform data into json objects
    ohlc_data = json.loads(pattern.findall(company_data)[5])
    volume_data = json.loads(pattern.findall(company_data)[6])
    ohlcv = []

    #merge ohlc and volume data into one list
    for price, volume in zip(ohlc_data, volume_data):
        price.append(volume[1])
        ohlcv.append(price)
    store_data(ohlcv, comp_tick)

    
def get_data(company):
    comp_tick = company.split("-")[0].upper()
    print(company)
    try:
        response = requests.get(f'https://www.jamstockex.com/trading/instruments/?instrument={company}')
        parse(response.text, comp_tick)
    except Exception as e:
        print("Issue is: " + str(e))


            
def scrape(event, context):
    with ThreadPoolExecutor() as executor:
        executor.map(get_data, tickers)
    coll.update_one({"name": "meta"}, {"$set": {"last_updated": int(time.time())*1000}})  
 
scrape(None, None)
