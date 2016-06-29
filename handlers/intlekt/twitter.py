import tweepy
import config
import logging
from flask import redirect
from flask import session
from flask import request
import urllib.parse


def twitter_token():
    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY,
                               config.TWITTER_CONSUMER_SECRET,
                               config.BASE_HOSTNAME + "/api/twitter/upgradeToken")
    redirect_url = ''
    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        logging.exception("message")
        print('Error! Failed to get request token.')

    redirect_url += "&oauth_callback=" + config.BASE_HOSTNAME \
                    + "/api/twitter/upgradeToken"

    session["request_token"] = auth.request_token
    return redirect(redirect_url, 302)


def twitter_upgradeToken():
    verifier = request.args["oauth_verifier"]
    print(verifier)
    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY,
                               config.TWITTER_CONSUMER_SECRET,
                               config.BASE_HOSTNAME + "/api/twitter/upgradeToken")
    token = session.get('request_token')
    auth.request_token = token

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print('Error! Failed to get access token.')

    print(auth.access_token)
    print(auth.access_token_secret)

    return redirect("/", 302)


def twitter_home_timeline():
    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY,
                               config.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(config.TWITTER_TEST_ACCESS_TOKEN,
                          config.TWITTER_TEST_ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    public_tweets = api.home_timeline()
    for tweet in public_tweets:
        print(tweet.text)

    return "OK"
