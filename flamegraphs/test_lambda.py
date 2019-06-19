import time
import os
import warnings
from s3fs import S3FileSystem
import pyarrow as pa
import pyarrow.parquet as pq
from bs4 import BeautifulSoup, NavigableString, Tag

def get_tweets_from_html(html_doc):
    """
      Per reference to code from :
      Logic changed to use PyArrow Arrays
      https://github.com/gutfeeling/twitass/blob/master/scraper.py
      :html_doc: Path of HTML document
      :return: List of PyArrow Array objects with parsed HTML attributes
    """
    soup = BeautifulSoup(open(html_doc))
    tweet_soup_list = soup.find_all("div", {"class" : "original-tweet"})
    try:
        ids = [int(tweet_soup["data-tweet-id"]) for tweet_soup in tweet_soup_list]
    except:
        ids = [int(tweet_soup["data-retweet-id"]) for tweet_soup in tweet_soup_list]
    try:
        tweet_ids = [int(tweet_soup["data-tweet-id"]) for tweet_soup in tweet_soup_list]
        user_ids = [int(tweet_soup["data-user-id"]) for tweet_soup in tweet_soup_list]
        usernames = [tweet_soup["data-name"] for tweet_soup in tweet_soup_list]
        screenhandles = [tweet_soup["data-screen-name"] for tweet_soup in tweet_soup_list]
        user_hrefs = [tweet_soup.find(
            "a",{"class" : "account-group"})["href"]
            for tweet_soup in tweet_soup_list]
        tweet_permalinks = [tweet_soup["data-permalink-path"] for tweet_soup in tweet_soup_list]
        tweet_languages = [tweet_soup.find(
            "p", {"class" : "tweet-text"})['lang']
            for tweet_soup in tweet_soup_list]
        tweet_times = [tweet_soup.find(
            "a",{"class" : "tweet-timestamp"})["title"]
            for tweet_soup in tweet_soup_list]
        tweet_timestamps = [tweet_soup.find(
            "span",{"class" : "_timestamp"})["data-time-ms"]
            for tweet_soup in tweet_soup_list]
        retweets = [int(tweet_soup.find(
            "span",{"class" : "ProfileTweet-action--retweet"}).find(
            "span", {"class" : "ProfileTweet-actionCount"})['data-tweet-stat-count'])
            for tweet_soup in tweet_soup_list]
        favorites = [int(tweet_soup.find(
            "span",{"class" : "ProfileTweet-action--favorite"}).find(
            "span", {"class" : "ProfileTweet-actionCount"})['data-tweet-stat-count'])
            for tweet_soup in tweet_soup_list]
        texts = [prettify_tweet_text(
            tweet_soup.find("p", {"class" : "tweet-text"}))
            for tweet_soup in tweet_soup_list]
    except Exception as e:
        print("Error while extracting information from tweet.")
        print(e)
    data = [
        pa.array(ids),
        pa.array(tweet_ids),
        pa.array(user_ids),
        pa.array(usernames),
        pa.array(screenhandles),
        pa.array(user_hrefs),
        pa.array(tweet_permalinks),
        pa.array(tweet_languages),
        pa.array(tweet_times),
        pa.array(tweet_timestamps),
        pa.array(retweets),
        pa.array(favorites),
        pa.array(texts)
    ]
    return data

def prettify_tweet_text(tweet_text_elements):
    """
      Code referenced from:
      https://github.com/gutfeeling/twitass/blob/4c7f25c51cad924f11b28d68a3f299df9e7f58b3/scraper.py#L169
    """
    tweet_text = ''
    for child in tweet_text_elements.children:
        if isinstance(child, NavigableString):
            tweet_text += child + " "
        elif isinstance(child, Tag):
            try:
                tag_class = child['class'][0]
                if tag_class == "twitter-atreply":
                    mention = ''.join([i.string for i in child.contents])
                    tweet_text += mention + " "
                elif tag_class == "twitter-hashtag":
                    hashtag = ''.join([i.string for i in child.contents])
                    tweet_text += hashtag + " "
                elif tag_class == "twitter-timeline-link":
                    if isinstance(child["href"], str):
                        tweet_text += child["href"] + " "
            except:
                if isinstance(child.string, str):
                    tweet_text += child.string + " "
    return " ".join(tweet_text.split())

def handler(file):
    """
    Lambda function to read raw HTML from S3 and save Parquet to a target
    """
    S3 = S3FileSystem(key=os.environ['ACCESS_KEY_ID'],
                      secret=os.environ['SECRET_ACCESS_KEY'])
    # html_doc = "s3://hidden-alphabet/{}".format(event['Records'][0]['s3']['object']['key'])
    filename = file.split('/')[-1]
    contents = get_tweets_from_html(html_doc)
    fields = [
        pa.field('id', pa.int64()),
        pa.field('tweet_id', pa.int64()),
        pa.field('user_id', pa.int64()),
        pa.field('username', pa.string()),
        pa.field('screenhandle', pa.string()),
        pa.field('user_href', pa.string()),
        pa.field('tweet_permalink', pa.string()),
        pa.field('tweet_language', pa.string()),
        pa.field('tweet_time', pa.string()),
        pa.field('tweet_timestamp', pa.string()),
        pa.field('retweets', pa.int64()),
        pa.field('favorites', pa.int64()),
        pa.field('tweet_text', pa.string())
    ]
    schema = pa.schema(fields)
    names = [
        'id',
        'tweet_id',
        'user_id',
        'username',
        'screenhandle',
        'user_href',
        'tweet_permalink',
        'tweet_language',
        'tweet_time',
        'tweet_timestamp',
        'retweets',
        'favorites',
        'tweet_text'
    ]
    batch = pa.RecordBatch.from_arrays(contents, names)
    table = pa.Table.from_batches([batch], schema)
    output_path = "s3://hidden-alphabet/datasets/webpages/processed/twitter.com/{}".format(filename)
    pq.write_to_dataset(table=table,
                        root_path=output_path,
                        filesystem=S3
    )
if __name__ == '__main__':
    import sys
    import io
    file = io.open(sys.argv[1])
    html = file.read()
    handler(html)