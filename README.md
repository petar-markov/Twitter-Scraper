# Twitter-Scraper

# IMPORTANT
## In this version, the function that is extracting the information from the Twitter API does not pick the whole JSON file. The information that is there for extraction is quite a lot, so we really do not want to get it at mass for now. With this version, we take the only the:

Username

Timestamp of the main tweet/re-tweet/comment

Tweet/Re-tweet/Comment

Bool marker to show if the data is from re-tweet or comment

Options to define whether or not to extract at all re-tweets and comments

## A simple Twitter Scraper that is created to be used with the default Twitter API (v1) for retrieving information only and nothing else.

This version is mostly focused on the data extract and not the overall formatting for any other algorithm. UTF-8 is used for encoding, so in case for any algorithmic usage of that data, a slight pre-processing might be needed, or an additional function ot be created to do that based on the needs.

Requirements needed for the script are stored in the "requirements.txt" and these can be installed easily with "pip install -r requirements.txt" - most of the times with no issues I believe.

For a quick test usage it is recommended to install and start this through a started python virtual env.


## Script usage

This version of the script is taking a couple of parameters that are being used in the procedures.
An example command :

"tweets.py test_file elonmusk tsvetkovpetar realdonaldtrump 1000 1 False"

In order to make use of the script the config.py file needs to have a working:
API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

Another option to use this is to have only the BEARER_TOKEN instead of the 4 keys in above. If this is used a slight change needs to be done within the function request calls.
Instead of using the "auth" option the "headers" should be used in exactly the same way. The function for creating the headers is also in the file.

These can be implemented to come from OS env. variables, but in the current version a "config.py" is available which is used for these. 

These can be requested and taken from the official Twitter website for that @: https://developer.twitter.com/en


Where:

tweets.py - File name of the script from the folder.

file_name: test_file.csv - File name of the output file that will be saved in the "output" folder.

users: elonmusk tsvetkovpetar realdonaldtrump - Twitter account names to get data for. NOTE: These should be always after the file name and before the numerical arguments following after.

items_per_user: 1000 - This is the number of elements retrieved per user. Elements in here could represent a - tweet, re-tweet, comment

with_retweets: 1 - This is a bool indicator whether or not a re-tweets should be included in the output.

no_replies: False - This is a bool indicator whether or not comments should be included in the output.

## Resource information from Twitter official website

Response formats	JSON

Requires authentication?	Yes

Rate limited?	Yes

Requests / 15-min window (user auth)	900

Requests / 15-min window (app auth)	1500

Requests / 24-hour window	100,000

Note: the 24-hour request limit is based on a rolling clock, beginning at the time of the first request and monitored for the next 24 hours.
