from multiprocessing.dummy import Pool
from bs4 import BeautifulSoup
import multiprocessing as mp

def tweet_element_to_dictionary(el):
    mentions = el.attrs.get('data-mentions')

    retweets_count = el\
            .find("span", {"class" : "ProfileTweet-action--retweet"})\
            .find("span", {"class" : "ProfileTweet-actionCount"})\
            .attrs.get('data-tweet-stat-count')

    favorites_count = el\
            .find("span", {"class" : "ProfileTweet-action--favorite"})\
            .find("span", {"class" : "ProfileTweet-actionCount"})\
            .attrs.get('data-tweet-stat-count')

    return {
        'user_id': el.attrs.get('data-user-id'),
        'user_name': el.attrs.get('data-name'),
        'user_href': 'twitter.com' + el.find("a", {"class": "account-group"}).attrs.get('href', '/'),
        'user_handle': el.attrs.get('data-screen-name'),
        'user_avatar_href': el.find('img', {'class': 'avatar'}).attrs.get('src'),

        'tweet_id': el.attrs.get('data-tweet-id'),
        'tweet_item_id': el.attrs.get('data-item-id'),
        'tweet_conversation_id': el.attrs.get('data-conversation-id'),
        'tweet_text_html': el.find("p", {"class" : "tweet-text"}).renderContents(),
        'tweet_text': el.find("p", {"class" : "tweet-text"}).text,
        'tweet_time': el.find("a", {"class": "tweet-timestamp"}).attrs.get('title'),
        'tweet-nonce': el.attrs.get('data-tweet-nonce'),
        'tweet_language': el.find("p", {"class" : "tweet-text"}).attrs.get('lang'),
        'tweet_timestamp_ms': el.find("span",{"class" : "_timestamp"}).attrs.get("data-time-ms"),
        'tweet_permalink': el.attrs.get('data-permalink-path'),

        'mentions_count': 0 if mentions is None else len(mentions.split(' ')),
        'retweets_count': int(retweets_count),
        'favorites_count': int(favorites_count),

        'is_reply': el.attrs.get('data-has-parent-tweet') is not None,
        'is_retweet': el.attrs.get('data-retweet-id') is not None,

        'has_media': el.find('div', {"class": 'AdaptiveMediaOuterContainer'}) is not None,
        'has_mentions': mentions is not None,
        'has_quote_tweet': el.find('div', {'class': 'QuoteTweet'}) is not None
    }

def html_to_objects(html):
    document = BeautifulSoup(html, 'lxml')
    tweets = document.find_all("div", {"class" : "original-tweet"})

    pool = Pool(min(mp.cpu_count(), len(tweets)))
    objects = pool.map(tweet_element_to_dictionary, tweets)

    pool.close()
    pool.join()

    return objects
