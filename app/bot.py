from mastodon import Mastodon
import os
import datetime as dt
import pandas as pd
import json
import time
from html import unescape


def test_post():
    token = os.environ["ACCESS_TOKEN"]

    mastodon = Mastodon(
        access_token=token,
        api_base_url="https://botsin.space/"
    )

    mastodon.status_post("This is another test post.\n Can you believe it???",
                         spoiler_text="test 4",
                         visibility="unlisted")


def timestamp_to_unix_seconds(timestamp):
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
                    "unix_seconds": timestamp_to_unix_seconds(tweet["tweet"]["created_at"]),
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
        "unix_seconds": "int"
    })

    return tweets, tweet_dict, df


def get_or_create_output_sheet(directory: str, dataframe: pd.DataFrame):

    files_in_dir = os.listdir(directory)

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

    output = output.astype(
        dtype={
            "id_str": "str",
            "created_at": "object",
            "full_text": "object",
            "img1": "object",
            "img2": "object",
            "img3": "object",
            "img4": "object",
            "unix_seconds": "object",
            "content_warning": "str",
            "img1_caption": "str",
            "img2_caption": "str",
            "img3_caption": "str",
            "img4_caption": "str",
            "privacy": "str"
        }
    )

    return output


def make_year_offset_for_now(offset):
    tzinfo = dt.timezone(dt.timedelta(hours=0))
    utc_now = dt.datetime.now(tzinfo)

    time_then = dt.datetime(
        year=(utc_now.year - offset),
        month=utc_now.month,
        day=utc_now.day,
        hour=utc_now.hour,
        minute=utc_now.minute,
        second=utc_now.second,
        tzinfo=utc_now.tzinfo
    )

    return time_then


def get_profile(mastodon):
    return mastodon.me()


def set_profile(mastodon, then: dt.datetime, old_profile):
    disp_name = os.environ["PROFILE_NAME"].replace("%Y", str(then.year))
    description = os.environ["PROFILE_DESC"].replace("%Y", str(then.year))

    all_fields = old_profile["source"]["fields"]
    field_list = []
    need_to_add_year = True
    need_to_add_day = True

    old_year = old_day = ""

    new_year = str(then.year)
    new_day = then.strftime("%A")

    # Go through all fields, update the ones which are automatic
    for field in all_fields:
        if field["name"] == "The year is":
            old_year = field["value"]
            field_list.append((field["name"], new_year))
            need_to_add_year = False
        elif field["name"] == "The day is":
            old_day = field["value"]
            field_list.append((field["name"], new_day))
            need_to_add_day = False
        else:
            field_list.append((field["name"], field["value"]))

    # Fields weren't there? Add them if they'll fit!
    if len(field_list) < 4 and need_to_add_year:
        field_list.append(("The year is", new_year))

    if len(field_list) < 4 and need_to_add_day:
        field_list.append(("The day is", new_day))

    if (disp_name != old_profile["display_name"]) or \
       (description != old_profile["source"]["note"]) or \
       (new_day != old_day) or (new_year != old_year):

        me = mastodon.account_update_credentials(
            display_name=disp_name,
            note=description,
            fields=field_list
        )
        return me

    return old_profile


if __name__ == "__main__":

    # Set up Mastodon account credentials
    token = os.environ["ACCESS_TOKEN"]
    mastodon = Mastodon(
            access_token=token,
            api_base_url="https://botsin.space/"
        )

    # test_post()

    # Import the tweets file to json and pandas data frame
    file_dir = "files"
    archive_directory = f"{file_dir}/{os.environ['ARCHIVE_FOLDER']}"
    tweets, tweet_dict, df = tweets_import(archive_directory)

    # Sort by date
    df = df.sort_values(by=["unix_seconds"])

    # Check for output sheet; create if not found
    output_sheet = get_or_create_output_sheet(file_dir, df)

    # Fetch ID of next tweet
    then = make_year_offset_for_now(int(os.environ["YEAR_OFFSET"]))

    next_tweet = df.loc[df["unix_seconds"] > then.timestamp()].head(1)

    check_profile = 0

    while (next_tweet.shape[0] > 0):

        next_tweet_id = next_tweet["id_str"].values[0]

        # Build toot to prepare for sending

        # Check sheet for settings once a minute leading up to posting; do this until under a minute to posting
        # Whenever update found, update the built toot

        time_delta = next_tweet["unix_seconds"].values[0] - then.timestamp()

        first_time = True

        while (time_delta > 60) or first_time:

            # Every ten iterations (minutes), check the profile and maybe update
            if check_profile == 10:

                profile = get_profile(mastodon)
                profile = set_profile(mastodon, then, profile)
                check_profile = 0

            else:
                check_profile += 1

            # The output sheet is used to modify the output prior to posting
            output_sheet = get_or_create_output_sheet(file_dir, df)
            tweet_settings = output_sheet.loc[output_sheet["id_str"] == next_tweet_id]

            # Get privacy preferences and set them for the post

            privacy = tweet_settings["privacy"].values[0]

            tweet_is_reply = next_tweet["is_reply"].values[0]

            if privacy.upper() == "PUBLIC":
                visibility = "public"
            elif privacy.upper() == "UNLISTED":
                visibility = "unlisted"
            elif privacy.upper() == "PRIVATE":
                visiblity = "private"
            elif privacy.upper() == "SKIP":
                visibility = "skip"
            elif tweet_is_reply:
                visibility = os.environ["REPLY_PRIVACY"]
            else:
                visibility = os.environ["TWEET_PRIVACY"]

            # Get content warning, if one has been added, and set it for the post

            if (tweet_settings["content_warning"].values[0] != "nan"):
                spoiler = tweet_settings["content_warning"].values[0]
            else:
                spoiler = None

            if first_time:
                print(f"Posting in {time_delta} seconds:\n" +
                      f"Status: {tweet_dict[str(next_tweet['id_str'].values[0])]['tweet']['full_text']}\n" +
                      f"Privacy: {visibility}\n" +
                      f"Content Warning: {spoiler}\n")

            if time_delta > 60:
                time.sleep(60)

            # Refresh the time delta by also updating present - offset
            then = make_year_offset_for_now(int(os.environ["YEAR_OFFSET"]))
            time_delta = next_tweet["unix_seconds"].values[0] - then.timestamp()
            first_time = False

            # FOR TESTING - if you uncomment the below, it'll post instantly
            # time_delta = 0

        # Send toot at scheduled time, go back to fetch next ID
        time.sleep(time_delta)

        if visibility != "skip":

            post_text = tweet_dict[next_tweet["id_str"].values[0]]["tweet"]["full_text"]
            mastodon.status_post(post_text,
                                 visibility=visibility,
                                 spoiler_text=spoiler)

        then = make_year_offset_for_now(int(os.environ["YEAR_OFFSET"]))
        next_tweet = df.loc[df["unix_seconds"] > then.timestamp()].head(1)
