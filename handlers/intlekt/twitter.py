import tweepy
import config
import logging
from flask import redirect
from flask import session
from flask import request


def twitter_token():
    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY,
                               config.TWITTER_CONSUMER_SECRET,
                               "/twitter/swapToken")
    redirect_url = ''
    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        logging.exception("message")
        print('Error! Failed to get request token.')

    session["request_token"] = auth.request_token
    return redirect(redirect_url, 302)


def twitter_swapToken():
    verifier = request.args["oauth_verifier"]
    print(verifier)
    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY,
                               config.TWITTER_CONSUMER_SECRET)
    token = session.get('request_token')
    auth.request_token = token

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print('Error! Failed to get access token.')

    print(auth.access_token)
    print(auth.access_token_secret)

    return redirect("/", 302)
