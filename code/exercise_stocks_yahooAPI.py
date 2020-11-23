# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16

@author: Michael ODonnell

Course: DATA698, Final Research Project

Script Overview: 
    1. Uses yfinance to grab stock ticker data from public fitness companies
    2. Returns a dataframe with change in stock prices pre vs post COVID-19
"""

# import libraries
"""
# yfinance library
try:
    import yfinance
except ImportError:
    !pip install yfinance

# yahoofinancials library
try:
    import yahoofinancials
except ImportError:
    !pip install yahoofinancials
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from yahoofinancials import YahooFinancials

# define stocks
stocks = ['CLUB',
          'PLNT',
          'NLS',
          'PTON',  
          'HLF',  
          'HD',
          'LOW',
          'DKS',  
          'NKE',
          'UA',
          'LULU',
          'FIT']

industry = ['Commercial_Gym',
            'Commercial_Gym',
            'At_Home_Gym',
            'At_Home_Gym',
            'At_Home_Nutrition',
            'Build_Home_Gym',
            'Build_Home_Gym',
            'Build_Home_Gym',
            'Fitness_Apparel',
            'Fitness_Apparel',
            'Fitness_Apparel',
            'Fitness_Apparel']

# define start and end dates
stock = 'NLS'              # choose your stock here
start_date = '2019-01-01'   # choose your initial investment date
end_date = '2020-10-14'     # choose your exit date


# function that will create a dataframe for a single stock
def create_stock_df(stock, start, end):
    
    # get the data from yahoo finance
    df = yf.download(stock, 
                     start=start, 
                     end=end, 
                     progress=False)
    
    # add extra columns for day, stock title,
    # simple moving averages, and closing price average difference
    df['day'] = range(1, len(df) + 1)
    df['stock'] = stock
    df['SMA_5'] = df.iloc[:,4].rolling(window=5).mean()
    df['SMA_30'] = df.iloc[:,4].rolling(window=21).mean()
    df['SMA_91'] = df.iloc[:,4].rolling(window=43).mean()
    df['SMA_182'] = df.iloc[:,4].rolling(window=104).mean()
    df['shifted_close'] = df['Close'].shift(1)
    df['close_difference'] = df['Close'] - df['shifted_close']
    
    # reset the index
    df = df.reset_index()
    
    # return the dataframe
    return df


# function to create a dataframe with multiple stocks
def compare_stocks_df(stocks, start, end):
    
    # first, create empty dataframe
    columns = ['stock',
               'first_date',
               'first_value',
               'end_date',
               'end_value',
               'total_difference',
               'PreVsPost_COVID_3months',
               #'PreVsPost_COVID_6months',
               'PreVsPost_COVID_September']
    df = pd.DataFrame(columns=columns)
    
    # for each stock in list of stocks, get data
    for s in range(len(stocks)):
        temp_df = create_stock_df(stocks[s], start_date, end_date)
        COVID_day = (temp_df.loc[temp_df['Date'] == "2020-03-13"].reset_index())['day'][0]
        data = {'stock': [get_first_value(temp_df['stock'])],
               'first_date': [get_first_value(temp_df['Date'])],
               'first_value': [get_first_value(temp_df['Close'])],
               'end_date': [get_last_value(temp_df['Date'])],
               'end_value': [get_last_value(temp_df['Close'])],
               'total_difference': [get_last_value(temp_df['Close'])-get_first_value(temp_df['Close'])],
               'PreVsPost_COVID_3months': [(temp_df['SMA_5'][COVID_day+62] - temp_df['SMA_5'][COVID_day-62])/temp_df['SMA_5'][COVID_day-62]],
               #'PreVsPost_COVID_6months': [temp_df['SMA_5'][COVID_day+126] - temp_df['SMA_5'][COVID_day-126]],
               'PreVsPost_COVID_September': [(temp_df['SMA_30'][COVID_day+140] - temp_df['SMA_30'][COVID_day-113])/temp_df['SMA_30'][COVID_day-113]]
                }
        new_df = pd.DataFrame(data)
        df = df.append(new_df)
        #print(new_df.head(2))
    df = df.reset_index(drop=True)
    df['Industry'] = industry
    return df
        

# function to plot the stock dataframe's closing prices
def plot_stock_price(df):
    
    x = df['Date']
    y = df['Close']

    # plotting the points  
    plt.plot(x, y) 

    # naming the axes 
    plt.xlabel('date')
    plt.ylabel('price/share')

    # rotate the tick marks
    plt.xticks(rotation=70)

    # title
    plt.title('Stock Price over time') 

    # function to show the plot 
    plt.show()
    
one_stock = create_stock_df(stock, start_date, end_date)

all_stocks = compare_stocks_df(stocks, start_date, end_date)

all_stocks.to_csv('fitness_stocks_v1.csv')

#plot_stock_price(test_df)