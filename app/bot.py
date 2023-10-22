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


def is_reply(tweet: dict):
    # This is not really a surefire method to get replies
    if tweet["full_text"][0] == "@":
        return True
    else:
        return False


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
                    "usec": timestamp_to_usec(tweet["tweet"]["created_at"]),
                    "is_reply": is_reply(tweet["tweet"])
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


def get_or_create_output_sheet(directory: str, dataframe: pd.DataFrame):

    files_in_dir = os.listdir(directory)

    print(files_in_dir)

    if "output_sheet.xlsx" in files_in_dir:
        # Find the file, important it into Pandas, return the df
        output = pd.read_excel(f"{directory}/output_sheet.xlsx")

        # TODO: Far future, check to see if the df has tweets not
        #       found in the extant output sheet because that's an issue

    else:
        output = dataframe.assign(
                        content_warning="",
                        img1_caption="",
                        img2_caption="",
                        img3_caption="",
                        img4_caption="",
                        privacy=""
            )

        output.to_excel(f"{directory}/output_sheet.xlsx", index=False)

    return output

def make_year_offset_for_now(offset):
    tzinfo = dt.timezone(dt.timedelta(hours=0))
    real_now = dt.datetime.now(tzinfo)
    # TODO: not done yet

    return real_now


if __name__ == "__main__":
    # test_post()

    # Import the tweets file to json and pandas data frame
    archive_directory = "files/twitter 2022"
    file_dir = "files"
    tweets, tweet_dict, df = tweets_import(archive_directory)
    print(tweets[0])
    print(df.loc[df['id_str'] == "1604577768158674945"])

    print(tweet_dict["1001260139"])

    # Sort by date
    df = df.sort_values(by=["usec"])
    print(str(df["usec"].head(5)))

    # Check for output sheet; create if not found
    output_sheet = get_or_create_output_sheet(file_dir, df)
    print(output_sheet.head(5))

    # Fetch ID of next tweet

    # Build toot to prepare for sending

    # Check sheet for settings once a minute leading up to posting; do this until under a minute to posting
    # Whenever update found, update the built toot

    # Send toot at scheduled time, go back to fetch next ID
