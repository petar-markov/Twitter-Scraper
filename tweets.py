from config import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN

import sys
import time
import requests
from requests_oauthlib import OAuth1, OAuth2
import urllib
import csv

def make_header(bearer_token):
    """
    Bearer token can be used as well for the authorization, as 
    we will be only searching for Tweets. If this is used we no longer need
    to use the "auth" in the requests, instead we need to use "headers" in the same way.
    """
    headers = {"Authorization": f'Bearer {bearer_token}'}
    return headers

def make_auth(api_key, api_secret, access_token, access_token_secret):
    """
    By default OAuth1 is used with the 4 keys given in the input
    Whenever this is used, the "auth" needs to be gived to the requests as an "auth" argument
    """
    verify_url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    auth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    auth_response = requests.get(verify_url, auth = auth)
    if auth_response.status_code != 200:
        raise Exception("Something wen't wrong during authentication.")

    return auth
    
def build_url(**params):
    """
    No base URL specified as we will implement a functionality to get tweets and nothing else.

    Input username and then all the needed additional parameters.
    List of avaialble parameters:
    user_id, screen_name, since_id, count, max_id, trim_user, exclude_replies, include_rts, tweet_mode

    tweet_mode = extended - is to be always in use in order to extract the full text from the tweets

    Detailed infomration can be found on the official Twitter API doc at:
    https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline

    https://api.twitter.com/1.1/statuses/user_timeline.json? is the base URL 
    """
    # Example working URL:
    # https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=elonmusk&count=150&tweet_mode=extended&exclude_replies=true

    base_url = "https://api.twitter.com/1.1/statuses/user_timeline.json?"
    url = base_url + urllib.parse.urlencode(params)
    print(url)
    return url

def is_reply_marker(value):
    """
    A small function to give a bool output if the given value is None / Not None
    """
    if value:
        return "1"
    return "0"

def connect_to_endpoint(url, auth_details):
    response = requests.get(url, auth = auth_details)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception("Error during making the webservice call to the endpoint, check URL or authentication details.")

    return response.json()

def generate_csv(filename):
    """
    Giving an input only the file name for now.
    Give the current data extract format we put the header row in here,
    but it could vary if the data extract functionality is changed to
    get additional info from the API.

    For now this one is working only with the output folder and not a whole path given
    """
    #Making the output file with a date suffix + the gived file name as an input
    dt = time.localtime()
    path = "./output/" + filename + "_" + "".join([str(i) for i in dt[0:3]]) + "_" + "".join([str(i) for i in dt[3:7]]) + ".csv"
    csv_file = open(path, 'a', newline = '', encoding = 'utf-8')
    csv_writer = csv.writer(csv_file)

    csv_writer.writerow(['user', 'created_at', 'main_tweet_or_retweet', 'quoted_tweet', 'is_retweet', 'is_reply'])

    return csv_file, csv_writer

def extract_tweet_data(data_source, file_writer):
    for tweet in data_source:
        try:
            file_writer.writerow([tweet["user"]["screen_name"], 
                                tweet["created_at"][:19], 
                                tweet["retweeted_status"]["full_text"].encode('utf-8'), 
                                tweet["retweeted_status"]["quoted_status"]["full_text"].encode('utf-8'), 
                                "1", 
                                is_reply_marker(tweet["in_reply_to_status_id"])])
        except KeyError as e:
            if "retweeted_status" in str(e):
                file_writer.writerow([tweet["user"]["screen_name"], 
                            tweet["created_at"][:19], 
                            tweet["full_text"].encode('utf-8'), 
                            "", 
                            "0", 
                            is_reply_marker(tweet["in_reply_to_status_id"])])
            elif "quoted_status" in str(e):
                file_writer.writerow([tweet["user"]["screen_name"], 
                            tweet["created_at"][:19], 
                            tweet["retweeted_status"]["full_text"].encode('utf-8'), 
                            "", 
                            "1", 
                            is_reply_marker(tweet["in_reply_to_status_id"])])
            else:
                raise

def main(users = [], file_name = "data.csv", items_per_user = 50, with_retweets = 1, no_replies = True):
    """
    users is a list that should have target Twitter user names as strings, separated by commas
    items_per_user by default 50, this is the amount of information rows per user retrieved from the API

    """

    auth = make_auth(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    #Initialize the csv file and create a writer for it
    csv_file, csv_writer = generate_csv(file_name)
    
    for user in users:
        tweets_retrieved = 0

        #Build initial URL 
        url = build_url(screen_name = user, 
                        tweet_mode = 'extended',
                        count = items_per_user, 
                        include_rts = with_retweets, 
                        exclude_replies = no_replies)

        response = connect_to_endpoint(url, auth)
        tweets_retrieved += len(response)

        extract_tweet_data(response, csv_writer)

        #Make sure that if the user has a limited amount of tweets we do not go
        # in infinite loop.
        if (tweets_retrieved < items_per_user) and (tweets_retrieved != response[0]["user"]["statuses_count"]):
            while True:
                #Get the max ID from the initial API call to continue further
                #There is an API limitation to get maximum of 200 items per call, so
                #here that is a workaround for that limitation.
                current_max_id = response[-1]["id_str"]
                url = build_url(screen_name = user, 
                                tweet_mode= 'extended', 
                                count = items_per_user - tweets_retrieved, 
                                include_rts = with_retweets, 
                                exclude_replies = no_replies, 
                                max_id = current_max_id)
                
                response = connect_to_endpoint(url, auth)
                extract_tweet_data(response, csv_writer)
                tweets_retrieved += len(response)

                if tweets_retrieved == items_per_user:
                    break
    
    csv_file.close()


if __name__ == "__main__":
    #We need explicit type cast for these
    file_name = sys.argv[1]
    users = [u for u in sys.argv[2:-3]]
    items_per_user = int(sys.argv[-3])
    with_retweets = int(sys.argv[-2])
    no_replies = sys.argv[-1]
    print(file_name)
    print(users)
    print(items_per_user)
    print(with_retweets)
    print(no_replies)
    main(users = users, 
        file_name = file_name,
        items_per_user = items_per_user, 
        with_retweets = with_retweets, 
        no_replies = no_replies)