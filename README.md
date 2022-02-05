# Jamaica Stock Exchange Web Scraper
This is a script to scrape stock & bond price data from the Jamaica Stock Exchange website.

## Motivation
I created this script because I found it difficult and time consuming to navigate the JSE website and find the information that I was looking for. I also wanted to use technical analysis tools on the data and the JSE website did not offer this feature.


## Tech/framework used
<b>Built with:</b>
- [Python 3](https://www.python.org)  
- [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup)
- [AWS](https://aws.amazon.com)
- [MongoDB](https://www.mongodb.com)

## Features
This script extracts all the relevant data on equities and bonds traded on the JSE. It then transforms the data into a JSON object and loads it into AWS S3 and/or MongoDB. From there it can be retrieved and used as the user sees fit. 

I've built a companion react app to display the data in a way that suited my needs. You can find that app [here](https://github.com/romallen/jse-chart-react).


## Installation
1. Clone this project and cd into it  
   `git clone https://github.com/romallen/jse-scraper.git`  
   `cd jse-scraper`
2. Add a Virtual Environment (Optional)  
  `python3 -m venv .venv` 
3. Activate the Virtual Environment (Optional)  
  `source .venv/bin/activate`
4. Install Requirements  
  `pip3 install -r requirements.txt`
  
## Tests
TBD

## How to use?
### Setup
Create a `.env` file in the root of the project.  

### MongoDB  
Add  `DB_URL=''` , `DB_NAME=''` & `COLL_NAME = ''` variables to the `.env` file and input values provided by MongoDB.  

*You can learn how to setup a MongoDB database [here](https://www.mongodb.com/basics/create-database)*


### AWS 




## License
MIT
