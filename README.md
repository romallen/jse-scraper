## Jamaica Stock Exchange Web Scraper
This is a script to scrape stock price data from the Jamaica Stock Exchange website.

## Motivation
I created this script because I found it difficult and time consuming to navigate the JSE website and find the information that I wanted. I also whated a to use technical analysis tools on the data and the JSE website did not offer that feature.

## Screenshots


## Tech/framework used
<b>Built with:</b>
- [Python 3](https://www.python.org)  
- [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup)
- [AWS](https://aws.amazon.com)
- [MongoDB] (https://www.mongodb.com/)


## Features
This script extracts all the relevant data on equities and bonds traded on the JSE. It thens transform the data into a JSON object and loads it into AWS Dynamo DB and/or MongoDB. From there it can be retrieved and used as the user sees fit. 

I've built a companion react native app to display the data in a way that suit my needs. You can find that app [here](https://github.com/romallen/chart-app).

## Code Example
Show what the library does as concisely as possible, developers should be able to figure out **how** your project solves their problem by looking at the code example. Make sure the API you are showing off is obvious, and that your code is short and concise.

## Installation
After forking and cloning the repository run `pip3 install -r requirements.txt` to install the necessary modules 

## Tests
TBD

## How to use?
Create a `.env` file in the root of the project.
#MongoDB 
Add a `DB_URL=''` variable to the `.env` file and input the url provided by MongoDB.

#AWS


## License
MIT © [Romaine Allen]()
