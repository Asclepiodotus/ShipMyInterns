import requests
import tweepy
import pandas as pd
from textblob import TextBlob

api_key = 'cJrzb7vMpmwcWjcjlGwgml4LA'
api_key_secret = 'vpxPXgqs6tqdlFAxwtIHxTpwkPvWzasO7UkP1yMLGzgDvTTK1P'
access_token = '1614981109573455875-6ugt7B2bMTwpYROAcH45uQNuDvzDWc'
access_token_secret = 'lav31jIinX2jUcJvT6FgcSFz0iNOnaCooEbQ8R2crAzAC'
bearer_token = 'AAAAAAAAAAAAAAAAAAAAADMFlQEAAAAAzbTVRutp9gtOLGgFkRmwHZL0gsI%3DG8lQeRpTbDG55OJOtnbIA4BamIexQqRkosrGKKqvC5xq9F2evP'


def display_options():
    """
    Display all dataframe columns and handle chained assignment warnings.
    """
    pd.set_option('display.max_columns', 35)
    pd.set_option('display.width', 250000)
    pd.options.mode.chained_assignment = None  # default='warn'


def collect():
    """
    Function that connects to the Twitter API, using the Developer Keys and Tokens.
    After connecting, a query is given to the API, to request specified data fields.
    That query can be customized and isn't SQL.
    Once the API has returned the data that was requested, the function will store it in a dataframe variable.

    Source used:
    https://www.kirenz.com/post/2021-12-10-twitter-api-v2-tweepy-and-pandas-in-python/twitter-api-v2-tweepy-and-pandas-in-python/
    """
    print('Connecting to Twitter API...')
    client = tweepy.Client(bearer_token=bearer_token,
                           consumer_key=api_key,
                           consumer_secret=api_key_secret,
                           access_token=access_token,
                           access_token_secret=access_token_secret,
                           return_type=requests.Response,
                           wait_on_rate_limit=True)

    query = 'Tesla -is:retweet -is:quote lang:en'  # give me tweets with this keyword, minus retweets and minus quoted tweets.
    # Je kunt dus met lang:nl alleen tweets in het Nederlands krijgen
    # query = 'Tesla -is:retweet -is:quote'  # give me tweets with this keyword, minus retweets and minus quoted tweets.


    # get max. 100 tweets (can't exceed 100 according to Twitter Documentation).
    tweets = client.search_recent_tweets(query=query,
                                         tweet_fields=['id', 'author_id', 'text', 'lang', 'created_at'],
                                         max_results=100)

    # Save data as dictionary
    tweets_dict = tweets.json()

    # Extract "data" value from dictionary
    tweets_data = tweets_dict['data']

    # Transform to pandas Dataframe
    df = pd.json_normalize(tweets_data)
    return df


def sentiment_analysis(df):
    """
    This function adds several new columns to the dataframe, for the generation and storage of sentiment and subjectivity data.
    TextBlob is used to determine the scores, based on the tweet's text. Since this is an out-of-the-box solution,
    there's a chance that the scores aren't very accurate. Especially with languages that aren't English.

    Subjectivity_score: float value ranging from 0 to 1, where 0.0 is very objective and 1.0 is very subjective.
    Polarity_score: value ranging from -1 to 1, where -1 defines a negative sentiment and 1 defines a positive sentiment. 0 defines neutral.
    Subjectivity: textual value displaying how subjective or objective the text was (based on subjectivity_score).
    Polarity: textual value displaying the sentiment of the text (based on polarity_score).

    Polarity and subjectivity label categories can be customized. Multiple categories could be added.

    Sources used:
    https://towardsdatascience.com/my-absolute-go-to-for-sentiment-analysis-textblob-3ac3a11d524
    https://www.kdnuggets.com/2018/08/emotion-sentiment-analysis-practitioners-guide-nlp-5.html
    """
    # create necessary new columns in the dataframe
    df_sentiment = df
    df_sentiment['subjectivity_score'] = 0
    df_sentiment['polarity_score'] = 0
    df_sentiment['subjectivity'] = 'None'
    df_sentiment['polarity'] = 'None'

    # iterate over the dataframe index and rows, grab the text and generate scores and place those in the correct column
    for i, r in df_sentiment.iterrows():
        text = df_sentiment['text'][i]
        df_sentiment['subjectivity_score'][i] = TextBlob(text).subjectivity
        df_sentiment['polarity_score'][i] = TextBlob(text).polarity

    # iterate over the dataframe index and rows, grab the scores and create a label based on that score.
    for idx, rw in df_sentiment.iterrows():
        subjectivity_score = df_sentiment['subjectivity_score'][idx]
        polarity_score = df_sentiment['polarity_score'][idx]

        if subjectivity_score < 0.49:
            df_sentiment['subjectivity'][idx] = 'Objective'
        else:
            df_sentiment['subjectivity'][idx] = 'Subjective'

        if polarity_score < 0:
            df_sentiment['polarity'][idx] = 'Negative'
        elif polarity_score > 0:
            df_sentiment['polarity'][idx] = 'Positive'
        else:
            df_sentiment['polarity'][idx] = 'Neutral'

    print(df_sentiment)
    return df_sentiment


if __name__ == '__main__':
    display_options()
    df = collect()
    final_df = sentiment_analysis(df)
    # final_df.to_excel('twitter-data.xlsx')  # write data to excel-file.
    final_df.to_csv('twitter-data.csv')     # write data to csv-file
    print('Script Executed.')
