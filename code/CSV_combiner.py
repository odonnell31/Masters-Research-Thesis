# -*- coding: utf-8 -*-
"""
Created on Thu Nov 5 08:14:43 2020

@author: ODsLaptop

@title: CSV combiner
"""
#import needeed libraries
import datetime
import pandas as pd
import numpy as np
import glob

# to look at all CSV files in the directory


# combine all CSV's from a directory into one CSV
def combine_CSVs(filepath):
    # print all CSV's in filepath
    print(glob.glob(filepath))
    
    # combine all CSV's into one CSV
    all_episode_data = pd.DataFrame()
    for f in glob.glob(filepath):
        df = pd.read_csv(f)
        all_episode_data = all_episode_data.append(df,ignore_index=True)

    # print summary of new dataframe
    print(all_episode_data.info(verbose=False))

    # export new dataframe to CSV
    all_episode_data.to_csv("combined_CSVs.csv",index=False)