import tweepy
import config
import logging
import json
from bson import ObjectId
from flask import redirect, session
import pika
from pymongo import MongoClient
from time import strftime

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def twitter_token():
    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY,
                               config.TWITTER_CONSUMER_SECRET,
                               config.BASE_HOSTNAME + "/api/intlekt/twitter/upgradeToken")
    redirect_url = ''
    try:
        # see http://stackoverflow.com/questions/21465532/tweepy-authentication-vs-authorization
        redirect_url = auth.get_authorization_url(signin_with_twitter=True)
    except tweepy.TweepError:
        logging.exception("message")
        print('Error! Failed to get request token.')

    session["request_token"] = auth.request_token
    return redirect(redirect_url, 302)


def twitter_upgradeToken():
    from flask import request
    verifier = request.args["oauth_verifier"]
    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY,
                               config.TWITTER_CONSUMER_SECRET,
                               config.BASE_HOSTNAME + "/api/intlekt/twitter/upgradeToken")
    token = session.get('request_token')
    auth.request_token = token

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print('Error! Failed to get access token.')
        return "There was an error"

    API = api(auth.access_token, auth.access_token_secret)
    screenName = get_twitter_screen_name(API)
    save_access_token(screenName, auth.access_token, auth.access_token_secret)

    return redirect(config.BASE_HOSTNAME+"/home", 302)


def get_twitter_screen_name(API):
    me = API.me()
    return me.screen_name


def save_access_token(screen_name, access_token, access_token_secret):
    client = MongoClient()
    dbusers = client.dbusers
    user = dbusers.users.find_one({"apis.twitter.screen_name": screen_name})
    if user is None:
        user = { 'since': strftime("%Y-%m-%dT%H:%M:%S"),
                 'apis' : { 'twitter':
                     {
                        'screen_name': screen_name,
                        'access_token': access_token,
                        'access_token_secret': access_token_secret
                    }
                 }
               }
        dbusers.users.insert_one(user)
    else:
        user['apis']['twitter'] = {
            'screen_name': screen_name,
            'access_token': access_token,
            'access_token_secret': access_token_secret
        }
        dbusers.users.save(user)
    session["current_guest"] = JSONEncoder().encode(user)


def api(access_token, access_token_secret):
    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


def twitter_home_timeline():
    user = json.loads(session.get("current_guest"))
    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY,
                               config.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(user['apis']['twitter']['access_token'],
                          user['apis']['twitter']['access_token_secret'])

    api = tweepy.API(auth)

    public_tweets = api.home_timeline()
    for tweet in public_tweets:
        print(tweet.text)

    return [tweet.text for tweet in public_tweets]


def twitter_update():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            'localhost'))
    channel = connection.channel()

    user_info = json.loads(session['current_guest'])
    print("user_info", user_info)
    channel.basic_publish(exchange='twitter-updater-exchange',
                          routing_key='twitter-updater',
                          body=json.dumps(user_info['apis']['twitter']))
    print("sent update request to the queue'")

    return "OK, cool"


def test_endpoint():
    current_guest = session.get("current_guest")
    print(current_guest)
    return json.loads(current_guest)