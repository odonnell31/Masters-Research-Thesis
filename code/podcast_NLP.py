#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 10:02:00 2020

@author: MichaelODonnell

@project: script analyze all podcast and episode descriptions

@script: all supporting functions
"""

# import libraries
import numpy as np
import pandas as pd
import nltk
import matplotlib
import matplotlib.pyplot as plt
from datetime import date, timedelta 
import math
import scipy.stats as stats

# read CSV's
def read_podcast_descriptions(filepath):
    podcast_info_df = pd.read_csv(filepath)
    podcast_info_df = podcast_info_df.sort_values(['total_episodes', 'name'],
                                                    ascending = (False, False))
        
    return podcast_info_df

def read_episode_descriptions(filepath):
    episode_desc_df = pd.read_csv(filepath)
    episode_desc_df = episode_desc_df.sort_values(['release_date', 'podcast'],
                                                    ascending = (False, False))
        
    return episode_desc_df

# create podcast descriptions dataframe from dataframe
def create_podcast_df(df):
    # create a dataframe of only descriptions to tokenize
    info_df = (df['description']).dropna().reset_index()
    
    # lowercase all the text in your remarks
    info_df['description'] = info_df['description'].str.lower()
    
    # remove punctuation from descriptions
    info_df['description'] = info_df['description'].str.replace('[^\w\s]','')
    
    return info_df

# create episode descriptions dataframe from dataframe
def create_episode_df(df):
    # create a dataframe of only descriptions to tokenize
    desc_df = (df['description']).dropna().reset_index()
    
    # lowercase all the text in your remarks
    desc_df['description'] = desc_df['description'].str.lower()
    
    # remove punctuation from descriptions
    desc_df['description'] = desc_df['description'].str.replace('[^\w\s]','')
    
    return desc_df

# find number of episodes in all passed in podcasts
def number_of_episodes(df):
    print("episodes:", df['total_episodes'].sum())
    
# tokenize the descriptions
def tokenize_descriptions(df):
    # create descriptions text
    desc_txt = df['description'].str.lower().str.replace(r'\|', ' ').str.cat(sep=' ')
    
    # tokenize the descriptions
    word_txt_tokens = nltk.word_tokenize(desc_txt)
    word_tokens = df['description'].apply(nltk.word_tokenize)
    sentance_tokens = df['description'].apply(nltk.sent_tokenize)
    
    # remove stopwords from word_tokens and word_txt_tokens
    from nltk.corpus import stopwords
    english_stops = set(stopwords.words('english'))
    word_tokens = word_tokens.apply(lambda x: [item for item in x if item not in english_stops])
    word_txt_tokens = [word for word in word_txt_tokens if word not in english_stops]
    
    return word_txt_tokens, word_tokens, sentance_tokens

# print the most common words in the desciptions
def print_top_tokens(tokens_txt, top_N=25):

    word_dist = nltk.FreqDist(tokens_txt)
    
    print('Word Frequencies')
    print('=' * 60)
    rslt = pd.DataFrame(word_dist.most_common(top_N),
                        columns=['Word', 'Frequency'])
    print(rslt)
    print('=' * 60)
    
# return the most common words in the descriptions
def return_top_tokens(tokens_txt, top_N=25):

    word_dist = nltk.FreqDist(tokens_txt)
    rslt = pd.DataFrame(word_dist.most_common(top_N),
                        columns=['Word', 'Frequency'])
    return rslt

# find all words around a specific word
def print_words_around(tokens, word):
    import nltk.corpus  
    from nltk.text import Text
    print(Text(tokens).concordance(word))

# find similar words to a specific word
def print_similar_words(tokens, word):
    import nltk.corpus  
    from nltk.text import Text
    print(Text(tokens).similar(word))
    
# examine the context shared by 2 words
def print_common_contexts(tokens, word1, word2):
    import nltk.corpus  
    from nltk.text import Text
    print(Text(tokens).common_contexts([word1, word2]))

# print the count of distinct words
def count_distinct_words(tokens):
    print('Distinct words:', len(set(tokens)))
    
# print the lexical diversity of the remarks
def lexical_diversity(tokens):
    print('Lexical Diversity:', round(len(tokens)/len(set(tokens)), 2))

# print the most common bi-grams
def print_top_bigrams(tokens_txt, top_N=20):
    from nltk.corpus import webtext
    from nltk.collocations import BigramCollocationFinder
    from nltk.metrics import BigramAssocMeasures
    
    bcf = BigramCollocationFinder.from_words(tokens_txt)
    #print(bcf.nbest(BigramAssocMeasures.likelihood_ratio, top_N))
    
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    
    for k,v in sorted(bcf.ngram_fd.items(), key=lambda t:t[-1], reverse=True):
        if v>top_N:
            print(k,v)
            
# return the most common bi-grams
def return_top_bigrams(tokens_txt, top_N=20):
    from nltk.corpus import webtext
    from nltk.collocations import BigramCollocationFinder
    from nltk.metrics import BigramAssocMeasures
    
    # collect bigrams
    bcf = BigramCollocationFinder.from_words(tokens_txt)
    
    # put bigrams into a dataframe
    rslt = pd.DataFrame(data = bcf.ngram_fd.items(),
                        columns = ['Bigram', 'Frequency'])
    
    # sort the dataframe by frequency
    rslt = rslt.sort_values(by=['Frequency'], ascending = False).reset_index(drop=True)
    
    # filter for only top bigrams
    if len(rslt) >= 25:
        rslt = rslt[0:25]
        
    else:
        rslt = rslt[0:10]
    
    return rslt

# return the most common tri-grams
def return_top_trigrams(tokens_txt, top_N=10):
    from nltk.corpus import webtext
    from nltk.collocations import TrigramCollocationFinder
    from nltk.metrics import TrigramAssocMeasures
    
    tcf = TrigramCollocationFinder.from_words(tokens_txt)

    # put trigrams into a dataframe
    rslt = pd.DataFrame(data = tcf.ngram_fd.items(),
                        columns = ['Trigram', 'Frequency'])
    
    # sort the dataframe by frequency
    rslt = rslt.sort_values(by=['Frequency'], ascending = False).reset_index(drop=True)
    
    # filter for only top trigrams
    if len(rslt) >= 25:
        rslt = rslt[0:25]
        
    else:
        rslt = rslt[0:7]
    
    return rslt

# create a dispersion plot
def top_tokens_dispersion(tokens_txt):
    
    from nltk.corpus import gutenberg
    from nltk.text import Text
    
    word_dist = nltk.FreqDist(tokens_txt)
    
    rslt = pd.DataFrame(word_dist.most_common(10),
                        columns=['Word', 'Frequency'])
    
    print(Text(tokens_txt).dispersion_plot([rslt['Word'][0], rslt['Word'][1],
                                    rslt['Word'][2], rslt['Word'][3],
                                    rslt['Word'][4], rslt['Word'][5]]))
    
# return the most common words in the descriptions
def count_terms(tokens_txt, set_of_words):
    counter = 0
    for w in set_of_words:
        word_count = tokens_txt.count(w)
        counter = counter + word_count
    return counter

# function to setup hypothesis test for podcast descriptions pre vs post COVID
def podcast_description_hypothesis_test(csv, list_of_words, alpha, title = "hypothesis test"):
    
    # first, read in the csv
    # 'data/final_datasets/relevant_episode_data_v2.csv'
    episode_desc_df = read_episode_descriptions(csv)
    preCOVID_episode_desc_df = episode_desc_df[pd.to_datetime(episode_desc_df['release_date']) < '2020-03-13']
    postCOVID_episode_desc_df = episode_desc_df[pd.to_datetime(episode_desc_df['release_date']) >= '2020-03-13']
    
    # format description column for tokenization
    desc_df = create_episode_df(episode_desc_df)
    preCOVID_df = create_episode_df(preCOVID_episode_desc_df)
    postCOVID_df = create_episode_df(postCOVID_episode_desc_df)
    
    # tokenize all 3 dataframes
    episode_tokens = tokenize_descriptions(desc_df)
    preCOVID_tokens = tokenize_descriptions(preCOVID_df)
    postCOVID_tokens = tokenize_descriptions(postCOVID_df)
    
    # create final dataframes for analyses
    episode_dataset = pd.DataFrame(episode_tokens[1])
    preCOVID_dataset = pd.DataFrame(preCOVID_tokens[1])
    postCOVID_dataset = pd.DataFrame(postCOVID_tokens[1])
    
    # add number of exercise terms to each row in above datasets
    episodes_terms = []
    for i in range(len(episode_dataset)):
        episodes_terms.append(count_terms(episode_dataset['description'][i], list_of_words))
    episode_dataset['number_of_words'] = episodes_terms
    
    preCOVID_terms = []
    for i in range(len(preCOVID_dataset)):
        preCOVID_terms.append(count_terms(preCOVID_dataset['description'][i], list_of_words))
    preCOVID_dataset['number_of_words'] = preCOVID_terms
    
    postCOVID_terms = []
    for i in range(len(postCOVID_dataset)):
        postCOVID_terms.append(count_terms(postCOVID_dataset['description'][i], list_of_words))
    postCOVID_dataset['number_of_words'] = postCOVID_terms
    
    # find mean, standard deviation, and count of pre-COVID-19 exercise terms
    preCOVID_mean =  preCOVID_dataset['number_of_words'].mean()
    preCOVID_sd = preCOVID_dataset['number_of_words'].std()
    preCOVID_episodes = len(preCOVID_dataset['number_of_words'])
    
    # find mean, standard deviation, and count of post-COVID-19 exercise terms
    postCOVID_mean =  postCOVID_dataset['number_of_words'].mean()
    postCOVID_sd = postCOVID_dataset['number_of_words'].std()
    postCOVID_episodes = len(postCOVID_dataset['number_of_words'])
    
    # use scipy to get test statistic and p-value
    hyp_test = stats.ttest_ind(postCOVID_dataset['number_of_words'],preCOVID_dataset['number_of_words'], equal_var=False)
    t_statistic = hyp_test[0]
    p_value = hyp_test[1]
    
    # print findings
    print("words tested:", list_of_words)
    print("variance of postCOVID:", round(postCOVID_dataset['number_of_words'].var(), 2))
    print("variance of preCOVID:", round(preCOVID_dataset['number_of_words'].var(), 2))
    print("difference in means = ", round((postCOVID_mean-preCOVID_mean), 3))
    print("t = ", round(t_statistic, 3))
    print("p = ", round(p_value, 3))
    print("alpha = ", str(alpha))
    if stats.ttest_ind(postCOVID_dataset['number_of_words'],preCOVID_dataset['number_of_words'], equal_var=False)[1] < alpha:
        print("Hypothesis result: REJECT the null hypothesis")
    else:
        print("Hypothesis result: cannot reject the null hypothesis")
        
    # export dataset
    postCOVID_dataset['post_COVID'] = 1
    preCOVID_dataset['post_COVID'] = 0
    df = preCOVID_dataset
    df = preCOVID_dataset.append(postCOVID_dataset)
    df.to_csv(f"{title}_data.csv")


# define endurance exercise words
endurance_words = ['running', 'run', 'cycling', 'cycle', 'biking', 'bike',
                   'swimming', 'swim', 'walking', 'walk', 'jogging', 'jog']

running_words = ['running', 'run', 'jogging', 'jog']

cycling_words = ['cycling', 'cycle', 'biking', 'bike']

swimming_words = ['swimming', 'swim', 'freestyle', 'breaststroke', 'butterfly', 'backstroke']

walking_words = ['walking', 'walk']

weightlifting_words = ['dumbbell', 'dumbbells', 'barbell', 'barbells',
                       'kettlebell', 'kettlebells', 'squat', 'press',
                       'bench', 'deadlift', 'lift', 'lifting']

crossfit_words = ['wod', 'box', 'amrap', 'afap']

yoga_words = ['yoga', 'yogi', 'meditation', 'stretching']