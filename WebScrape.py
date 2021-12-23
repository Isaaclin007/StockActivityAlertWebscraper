from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date, timedelta
import pandas as pd
import yfinance as yf
import schedule
import time
from textmagic.rest import TextmagicRestClient
#You can get yourself rate limited/blacklisted. Again because the libraries and
# unofficial APIs sometimes scrape data, they could get rate limited or
#blacklisted by Yahoo Finance at any time
today = date.today()
d1 = today.strftime("%Y-%m-%d")
end_date = d1
d2 = date.today() -  timedelta(days=360)
d2 = d2.strftime("%Y-%m-%d")
start_date = d2
data = yf.download('TSLA', start = start_date, end = end_date, progress = False)
data["Date"]=data.index
data = data[["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]]
data.reset_index(drop = True, inplace = True)
# writing data frame to a CSV file, this is for a possible ML application (not sure if this is super applicable to this project)
# data.to_csv('historical.csv')



#getting outline data on the past data
days = int(input("How many days back do you want to go to establish support/resistance?"))

data_scope_max = data[-days:].max(axis = 0)
data_scope_min = data[-days:].min(axis = 0)

price_max =float(data_scope_max.High)
price_min =float(data_scope_min.Low)
price_flag = False

#run the following code once per minute
def job():
    global price_max
    global price_min
    global price_flag
    if False==price_flag:
        print('polling')
        #opening up the webpage and running it through BeautifulSoup
        optionsUrl = 'https://www.google.com/finance/quote/TSLA:NASDAQ'
        optionsPage = urlopen(optionsUrl)
        soup = BeautifulSoup(optionsPage, 'html.parser')
        #finding the div that contains the value
        price_box = soup.find('div', attrs={'class':'YMlKec fxKbKc'})
        price = float((price_box.text.strip()[1:]).replace(',', ''))
#        print('price max is: ' + str(price_max) + ' price min is: ' + str(price_min) + ' the price is ' + str(price))
        #complete one implied volatility calculation
        if(price>price_max or price<price_min):
            #alert1 + gen report
            print("If you have filled out the correct TextMagic login info, it will send a text message to your phone now")
            price_flag = True
            if price > price_max:
                price_max = price
            if price < price_min:
                price_min = price
            #note TextMagic account is private, input your own Username and Token to complete SMS message
##            username = "cchandel2002"
##            token = "*************"
##            client = TextmagicRestClient(username, token)
##            message = client.messages.create(phones="2267004807", text="{0} day support or resistance has been broken ".format(days))

def reset():
    global price_flag
    price_flag = False
    print('reset')
schedule.every(10).seconds.do(job)
schedule.every(30).minutes.do(reset)
while True:
    schedule.run_pending()
    time.sleep(1)


