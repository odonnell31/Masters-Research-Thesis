# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 17:48:51 2020

@author: ODsLaptop
"""

# load libraries
import pandas as pd
import datetime

def add_week_numbers(csv):
    
    # load CSV as s dataframe
    df = pd.read_csv(csv)
    
    # add year, month, and week numbers to dataframe
    df['year_number'] = pd.to_datetime(df['release_date']).dt.year
    df['month_number'] = pd.to_datetime(df['release_date']).dt.month
    df['week_number'] = pd.to_datetime(df['release_date']).dt.week
    df['year_week'] = df['year_number'].map(str) + df['week_number'].map(str)
    df['year_month'] = df['year_number'].map(str) + df['month_number'].map(str)
    
    # export dataframe to a csv
    df.to_csv("data_v4.csv", index=False)
