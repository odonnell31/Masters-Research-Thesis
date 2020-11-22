# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 21:34:23 2020

@author: MichaelODonnell

@title: spotify API for podcast data
"""

#import needeed libraries
import requests
import base64
import datetime
import pandas as pd
from urllib.parse import urlencode
import json

# enter your client id and client secret
client_id = "replace with your client id here"
client_secret = "replace with your client secret here"

### Connecting to Spotify ###
# create SpotifyAPI class
class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = 'https://accounts.spotify.com/api/token'
    
    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        
    def get_client_credentials(self):
        """
        Returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        
        if client_secret == None or client_id == None:
            raise Exception("you must set client_id and client_secret")
        
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()
        
    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        
        return {
            'Authorization': f"Basic {client_creds_b64}"
        }
    
    def get_token_data(self):
        return {
            'grant_type': 'client_credentials'
        }
        
    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        
        r = requests.post(token_url, data = token_data, headers = token_headers)

        if r.status_code not in range(200,299):
            raise Exception("Could not authenticate client..")
            # return False
        
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in'] #seconds
        expires = now + datetime.timedelta(seconds = expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
            
        return True
    
    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token
    
    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {
            'Authorization': f"Bearer {access_token}"
        }
        return headers
    
    def get_resource(self, lookup_id, resource_type = 'shows', version='v1', market = 'US'):
        if resource_type == 'shows':
            endpoint = f"https://api.spotify.com/{version}/shows/{lookup_id}/episodes"
        else:
            endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        #endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        print(lookup)
        if r.status_code not in range(200,299):
            return {}
        return r.json()
    
    ### Searching Spotify ###
    # search Spotify by name
    def search(self, query, search_type = 'artists', market = 'US'):
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        data = urlencode({'q': query, 'type': search_type.lower(), 'market': market})
        lookup_url = f"{endpoint}?{data}"
        print(lookup_url)
        r = requests.get(lookup_url, headers = headers)
        if r.status_code not in range(200,299):
            return "somethings wrong"
        return r.json()
    
    ### Retrieving Music Data ###
    # get album information
    def get_album(self, _id):
        return self.get_resource(_id, resource_type='albums')
    
    # get artist information
    def get_artist(self, _id):
        return self.get_resource(_id, resource_type='artists')
    
    
    
    ### Retrieving Podcast Data ###
    # get the following columns about a podcast:
        #name, publisher, total_episodes, id, media_type,
        #description, external_urls, uri
    def get_podcast_info_by_id(self, showid, market = 'US'):
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/shows"
        data = urlencode({'ids': showid, "market": market})
        lookup_url = f"{endpoint}?{data}"
        #print(lookup_url)
        r = requests.get(lookup_url, headers = headers)
        if r.status_code not in range(200,299):
            return "somethings wrong"
        
        raw_json = r.json()
        
        podcast_dict = {'name': raw_json['shows'][0]['name'],
            'publisher': raw_json['shows'][0]['publisher'],
            'total_episodes': raw_json['shows'][0]['total_episodes'],
            'id': raw_json['shows'][0]['id'],
            'media_type': raw_json['shows'][0]['media_type'],
            'description': raw_json['shows'][0]['description'],
            'external_urls': raw_json['shows'][0]['external_urls'],
            'uri': raw_json['shows'][0]['uri']}
        
        return podcast_dict
    
    # get multiple podcasts info in a dataframe
    def multiple_podcasts_info(self, list_of_ids):
        # create empty dataframe
        podcasts_info_df = pd.DataFrame(columns = ['name', 'publisher','total_episodes',
                                                     'id','media_type', 'description',
                                                     'external_urls', 'uri'])
        
        # grab podcast info from each id and append to dataframe
        for i in list_of_ids:
            temp_dict = self.get_podcast_info_by_id(i)
            df = pd.DataFrame(temp_dict, columns = ['name', 'publisher',
                                                  'total_episodes', 'id',
                                                  'media_type', 'description',
                                                  'external_urls', 'uri'])
            #print(df)
            podcasts_info_df = podcasts_info_df.append(df)
            
        podcasts_info_df = podcasts_info_df.reset_index(drop=True)
        
        return podcasts_info_df
    
    # get podcast episodes from a show
    def get_podcast_episodes_by_id(self, showid, num_episodes = 10, market = 'US'):
        headers = self.get_resource_header()
        endpoint = f"https://api.spotify.com/v1/shows/{showid}/episodes?offset=0&limit={num_episodes}&market=US"
        #data = urlencode({'ids': showid, "market": market})
        lookup_url = f"{endpoint}"
        #print(lookup_url)
        r = requests.get(lookup_url, headers = headers)
        if r.status_code not in range(200,299):
            return "somethings wrong..."
        
        raw_json = r.json()
    
        episode_df = pd.DataFrame(columns = ['podcast', 'name','release_date','duration_min',
                                     'external_urls','id', 'language',
                                     'release_date_precision', 'uri','description'])
    
        podcast_name = self.get_podcast_info_by_id(showid)['name']

        for i in range(num_episodes):
            # create a dict with the data
            temp_dict = {'podcast': podcast_name,
                       'name': raw_json['items'][i]['name'],
                       'release_date': raw_json['items'][i]['release_date'],
                       'duration_min': round((raw_json['items'][i]['duration_ms'])/60000,2),
                       'external_urls': raw_json['items'][i]['external_urls'],
                       'id': raw_json['items'][i]['id'],
                       'language': raw_json['items'][i]['language'],
                       'release_date_precision': raw_json['items'][i]['release_date_precision'],
                       'uri': raw_json['items'][i]['uri'],
                       'description': raw_json['items'][i]['description']}

            df = pd.DataFrame(temp_dict, columns = ['podcast','name','release_date','duration_min',
                                     'external_urls','id', 'language',
                                     'release_date_precision', 'uri','description'])
            episode_df = episode_df.append(df)

        episode_df = episode_df.reset_index(drop=True)
        return episode_df
    
    # get all podcast episodes from a show
    def get_all_podcast_episodes(self, showid, market = 'US'):
        
        headers = self.get_resource_header()
        
        podcast_name = self.get_podcast_info_by_id(showid)['name']
        num_episodes = self.get_podcast_info_by_id(showid)['total_episodes']
        
        limit = 25
        offset = 0
        num_runs = num_episodes//limit
        
        episode_df = pd.DataFrame(columns = ['podcast', 'name','release_date','duration_min',
                             'external_urls','id', 'language',
                             'release_date_precision', 'uri','description'])
        
        for i in range(num_runs):
        
            endpoint = f"https://api.spotify.com/v1/shows/{showid}/episodes?offset={offset}&limit={limit}&market=US"
            lookup_url = f"{endpoint}"
        
            r = requests.get(lookup_url, headers = headers)
            if r.status_code not in range(200,299):
                return "somethings wrong..."
            
            raw_json = r.json()
        


            for i in range(limit):
                # create a dict with the data
                temp_dict = {'podcast': podcast_name,
                           'name': raw_json['items'][i]['name'],
                           'release_date': raw_json['items'][i]['release_date'],
                           'duration_min': round((raw_json['items'][i]['duration_ms'])/60000,2),
                           'external_urls': raw_json['items'][i]['external_urls'],
                           'id': raw_json['items'][i]['id'],
                           'language': raw_json['items'][i]['language'],
                           'release_date_precision': raw_json['items'][i]['release_date_precision'],
                           'uri': raw_json['items'][i]['uri'],
                           'description': raw_json['items'][i]['description']}
    
                df = pd.DataFrame(temp_dict, columns = ['podcast','name','release_date','duration_min',
                                         'external_urls','id', 'language',
                                         'release_date_precision', 'uri','description'])
                episode_df = episode_df.append(df)
            
            offset = offset + limit

        episode_df = episode_df.reset_index(drop=True)
        return episode_df
    
 
    
    
### Recurring API Calls for Database ###

# instantiate spotifyAPI class object
spotify = SpotifyAPI(client_id, client_secret)
    
# define podcast id's

## Running Podcasts
Trail_Runner_Nation = '603z2wAQ73kcqTbM1pTl74'
The_Running_Public = '2vUYerXBNhRDPcaINbYK8I'
Another_Mother_Runner = '7HlsUrk4KVfMrX0dcqkT8e'
The_Running_Pod = '2PacGg6zS1UZzOtS680MrR'
Run_to_the_Top_Podcast = '4sIXIw0CbMW0on5zKXAet1'
The_Strength_Running_Podcast = '1ZkJ0i0utCvF8NidUvfyYW'
Running_Lean = '72KqZFtcRSoZFpPVTgJYvZ'
RunBuzz_Running_Podcast = '43fRWm1WJwVZZ9kGnfIngU'
Running_Things_Considered = '7L5aLeFO5zDMcinUfrm8oV'
The_Runners_Zone = '4qMTmxMVJAKuUk5K7zZz55'
Runners_of_NYC = '4DD2jtIBEcyVohfiimggvM'
The_Runners_World_Show = '5LYUDIwTqW0vogUVpicWto'
Not_Real_Runners = '3ysDuOiqvtPhRav34aMPwW'
Coaching_Runners = '79ibGRJzwgqUyLdOT3IKvL'
Citius_Mag_Podcast = '70eINNmXl67VqorbTsMOaH'
UltraRunnerPodcast = '61xgBmYdeuyOT2fTPrzzIm'
Pace_the_Nation = '69eduxltbKTWRIG1lLxKe5'
Running_for_Real = '3W0HMvNKA3lVGzjxhrNR2L'
Run_Selfie_Repeat = '4CvnqmCQF0XeDnMHGwKwBy'
Cultra_Trail_Running = '44etXyR0WbJtmKRKrP7V6M'
Not_Your_Average_Runner_Podcast = '0V7QvU2g85OXdNMyXlUxSe'
BibRave_Podcast = '5wKB3zJNfsNpR0UULrc3Ci'
Trail_Running_Women = '3tcmWbYXlZ5xJgJ6x18BXJ'

## Crossfit and Weightlifting Podcasts
IST_Crossfit_Podcast = '7a2nsyURhSOFl6142v0NrI'
Align = '2MhCZyUIf8jdYGpbSWzTEu'
Mind_Muscle_Podcast = '7njrOvgJILJticGmSlZimQ'
Kyle_Kingsbury_Podcast = '48np1CmAhgejG9lWz4zzmG'
Corpus_Animus_Podcast = '4PhJcVrETVZ4YwgYg20yuF'
Misfit_Podcast = '77ZHkfmEtIzTgySTJDUoFn'
WODcast_Podcast = '2KfJ2DqIh7nKlOz5DVrda3'
Refined_Savage = '5cE7v8r2mQJS7OlrbP6CHT'
Shred_Crossfit_Podcast = '4Z2EbFyT0noKPkLdkH8I0a'
Froning_and_friends = '5wzVDmPQMWLGt41Qsjoviq'

## Fitness Podcasts
Trained = '4S5PahOirvvAuGBswLfNzh'
Jillian_Michaels_Show = '4VrcVlKG8AylvTQ0cALTlC'
Whoop_Podcast = '0yFoBgekRMM9lN0xMMczL7'
Mind_Pump = '4D3JFAh4ebj9lks9WOE2Vs'
Ben_Greenfield_Fitness = '4nN0MRFIdTsx3iMrsh9TYd'
Joe_DeFranco_Industrial_Strength = '6wl9a3uCFB8WUtJUe10yWP'
On_Purpose_Jay_Shetty = '5EqqB52m2bsr4k1Ii7sStc'
Bulletproof_Radio = '2mkB9OoukPVKCTKSuAIgCq'
AMRAP_Mentality = '1tp3xZbv5ehPaGH6JRsYad'
WAG_podcast = '4CLZibzMK2pIs9qrTUy5sr'
Brute_Strength_Podcast = '7fWY5SGpUE65RQDWhxAn58'
Barbend_Podcast = '10OyHgZW3FrnAIffUpvrdA'
Chasing_Excellence = '5DGoQinz8rbs6iG0UKsscT'
No_Meat_Athlete = '4dfCUNYJyhssXD29UDdxtq'
Muscle_For_Life = '3Vn2r4Nf0t6QDaWuJLp6dh'
Nine_to_Five_Fitness = '72mvH51A2oTeA7b9DtN4zX'

# create lists of id's

running_podcast_ids = [Trail_Runner_Nation,
                       The_Running_Public,
                       Another_Mother_Runner,
                       The_Running_Pod,
                       Run_to_the_Top_Podcast,
                       The_Strength_Running_Podcast,
                       Running_Lean,
                       RunBuzz_Running_Podcast,
                       Running_Things_Considered,
                       The_Runners_Zone,
                       Runners_of_NYC,
                       The_Runners_World_Show,
                       Not_Real_Runners,
                       Citius_Mag_Podcast,
                       UltraRunnerPodcast,
                       Pace_the_Nation,
                       Run_Selfie_Repeat,
                       Cultra_Trail_Running,
                       Not_Your_Average_Runner_Podcast,
                       BibRave_Podcast,
                       Trail_Running_Women]

crossfit_podcasts = [IST_Crossfit_Podcast,
                    Align,
                    Mind_Muscle_Podcast,
                    Kyle_Kingsbury_Podcast,
                    Corpus_Animus_Podcast,
                    Misfit_Podcast,
                    WODcast_Podcast,
                    Refined_Savage,
                    Shred_Crossfit_Podcast,
                    Froning_and_friends]

fitness_podcasts = [Trained,
                    Jillian_Michaels_Show,
                    Whoop_Podcast,
                    Mind_Pump,
                    Ben_Greenfield_Fitness,
                    Joe_DeFranco_Industrial_Strength,
                    On_Purpose_Jay_Shetty,
                    Bulletproof_Radio,
                    AMRAP_Mentality,
                    WAG_podcast,
                    Brute_Strength_Podcast,
                    Barbend_Podcast,
                    Chasing_Excellence,
                    No_Meat_Athlete,
                    Muscle_For_Life,
                    Nine_to_Five_Fitness]

### Recurring API Call for Shows' Info ###
def shows_info_spotifyAPI_call(podcast_ids_list):
    multiple_podcasts_df = spotify.multiple_podcasts_info(podcast_ids_list)
    return multiple_podcasts_df

### Recurring API Call for Episodes Info ###
def episodes_info_spotifyAPI_call(podcast_ids_list):
    
    # create empty dataframe
    all_episodes = pd.DataFrame(columns = ['podcast','name','release_date','duration_min',
                                     'external_urls','id', 'language',
                                     'release_date_precision', 'uri','description'])
    
    for i in podcast_ids_list:
        try:
            episodes_df = spotify.get_podcast_episodes_by_id(i, num_episodes = 15,
                                                             market = 'US')
        except:
            episodes_df = spotify.get_podcast_episodes_by_id(i, num_episodes = 10,
                                                             market = 'US')            
        
        ### query to put into database
        print(episodes_df)
        all_episodes = all_episodes.append(episodes_df).reset_index(drop=True)
        
    return all_episodes

### Recurring API Call for Latest Episode Info ###
def latest_episodes_spotifyAPI_call(podcast_ids_list):
    
    # create empty dataframe
    all_episodes = pd.DataFrame(columns = ['podcast','name','release_date','duration_min',
                                     'external_urls','id', 'language',
                                     'release_date_precision', 'uri','description'])
    
    for i in podcast_ids_list:
        try:
            episodes_df = spotify.get_podcast_episodes_by_id(i, num_episodes = 1,
                                                             market = 'US')
        except:
            episodes_df = spotify.get_podcast_episodes_by_id(i, num_episodes = 1,
                                                             market = 'US')            
        
        ### query to put into database
        print(episodes_df)
        all_episodes = all_episodes.append(episodes_df).reset_index(drop=True)
        
    return all_episodes

### Get all episodes from one podcast ###
def all_episodes_one_podcast(podcast_id):
    
    df = spotify.get_all_podcast_episodes(podcast_id)
        
    return df