import logging
from time import strftime

import pika
import tweepy
from bson.json_util import *
from flask import redirect, session
from pymongo import MongoClient

import config
from handlers.intlekt.twitter.Constants import *


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
    client = MongoClient()
    library_db = client.library
    screen_name = get_screen_name()
    user_collections = library_db[screen_name+"_collections"]
    iso_time = datetime.datetime.utcnow().isoformat()

    result = user_collections.insert_one(
        {
            "status": "draft",
            "stage": "init",
            "created": iso_time
        }
    )
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            RABBITMQ_HOST))
    channel = connection.channel()

    user_info = json.loads(session['current_guest'])
    request_info = user_info['apis']['twitter']
    request_info["collection_id"] = result.inserted_id
    request_info[REQUEST_TYPE]=DATASET_UPDATE_REQUEST_TYPE
    channel.basic_publish(exchange='async-workers-exchange',
                          routing_key='async-workers',
                          body=JSONEncoder().encode(request_info))

    return {'draft_created': JSONEncoder().encode(result.inserted_id)}

def twitter_similarities():
    return queue_request(SIMILARITY_COMPUTATION_REQUEST_TYPE)

def queue_request(request_type):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            RABBITMQ_HOST))
    channel = connection.channel()

    user_info = json.loads(session['current_guest'])
    request_info = user_info['apis']['twitter']
    request_info[REQUEST_TYPE]=request_type
    channel.basic_publish(exchange='async-workers-exchange',
                          routing_key='async-workers',
                          body=json.dumps(request_info))
    return {'message': 'request_sent'}

def test_endpoint():
    screen_name = get_screen_name()
    user_collections = MongoClient().library[screen_name+"_collections"]
    user_collection = user_collections.find_one({"_id": ObjectId("5798aafd421aa975bdc2e780")})
    return user_collection
    # client = MongoClient()
    # library = client.library
    # screen_name = get_screen_name()
    # all_resources = library[screen_name].find()
    # usls = {}
    # for doc in all_resources:
    #     if doc['expandedUrl'] is None: continue
    #     if doc['hashtags'] is not None:
    #         for kw in doc['hashtags']:
    #             add_keyword(library, doc, usls, kw)
    # all_resources = library.ckemmler_resources.find()
    # for doc in all_resources:
    #     if doc['expandedUrl'] is None: continue
    #     if doc['keywords'] is not None:
    #         for kw in doc['keywords'].split(","):
    #             add_keyword(library, doc, usls, kw)
    # return usls

def add_keyword(library, doc, usls, kw):
    results = library.usl.find({"KEYWORDS_EN.ORIGINAL": kw})
    for found in results:
        key = found["KEYWORDS_FR"]["ORIGINAL"][0]+" **"+found["_id"] + "*"
        if key in usls:
            usls[key].append(doc["expandedUrl"])
        else:
            usls[key] = [doc["expandedUrl"]]

def get_screen_name():
    user_info = json.loads(session['current_guest'])
    return user_info["apis"]["twitter"]["screen_name"]