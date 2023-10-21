from mastodon import Mastodon
import os
import datetime as dt
import pandas as pd
import json


def test_post():
    token = os.environ["ACCESS_TOKEN"]
    print(token)
    mastodon = Mastodon(
        access_token=token,
        api_base_url="https://botsin.space/"
    )

    mastodon.status_post("This is a test post.")


def timestamp_to_usec(timestamp):
    post_dt = dt.datetime.strptime(timestamp, "%a %b %d %H:%M:%S %z %Y")
    return post_dt.timestamp()


def tweets_import(directory):
    # Open the tweets.js file and parse it correctly
    rawfile = open(f"{directory}/data/tweets.js")
    rawtext = rawfile.read()
    json_text = rawtext.replace("window.YTD.tweets.part0 = ", "")

    # create the tweets list
    tweets = json.loads(json_text)

    # create tweet dict
    tweet_dict = dict()

    # Fill both the dict and df

    tweets_for_pd = []

    for tweet in tweets:
        tweet_dict[tweet["tweet"]["id_str"]] = tweet
        tweets_for_pd.append(
                {
                    "id_str": tweet["tweet"]["id_str"],
                    "created_at": tweet["tweet"]["created_at"],
                    "full_text": tweet["tweet"]["full_text"],
                    "img1": "",
                    "img2": "",
                    "img3": "",
                    "img4": "",
                    "usec": timestamp_to_usec(tweet["tweet"]["created_at"])
                }
        )
    # Create the df
    df = pd.DataFrame(tweets_for_pd)

    df = df.astype(dtype={
        "id_str": "object",
        "created_at": "object",
        "full_text": "object",
        "img1": "object",
        "img2": "object",
        "img3": "object",
        "img4": "object",
        "usec": "object"
    })

    return tweets, tweet_dict, df


if __name__ == "__main__":
    # test_post()

    # Import the tweets file to json and pandas data frame
    directory = "files/twitter 2022"
    tweets, tweet_dict, df = tweets_import(directory)
    print(tweets[0])
    print(df.loc[df['id_str'] == "1604577768158674945"])
    df = df.sort_values(by=["usec"])
    print(str(df["usec"].head(5)))
    print(tweet_dict["1604577768158674945"])
    # Sort by date

    # Check for output sheet; create if not found

    # Fetch ID of next tweet

    # Build toot to prepare for sending

    # Check sheet for settings once a minute leading up to posting; do this until under a minute to posting
    # Whenever update found, update the built toot

    # Send toot at scheduled time, go back to fetch next ID
