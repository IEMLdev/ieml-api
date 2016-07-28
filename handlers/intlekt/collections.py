from flask import session
import pika
from .Constants import *
from .twitter import JSONEncoder
from .twitter import get_screen_name
from pymongo import MongoClient
from bson.json_util import *
from config import *
from bson.objectid import ObjectId
from .io import push_server_event

def getPreTaggedDataset(collection_id):
    # retrieve the collection from the database and check what stage it's at
    # if the stage is "INITED", we're too early and we should throw an exception;
    # right after that comes "POPULATED" which means the dataset
    # hasn't been pre-tagged yet, so we then request that to be done asynchronously
    # and return an empty response. For other stages, we can return the dataset
    screen_name = get_screen_name()
    user_collections = MongoClient().library[screen_name+"_collections"]
    user_collection = user_collections.find_one({"_id": ObjectId(collection_id)})
    if user_collection is None:
        raise Exception ("No such collection: " + collection_id)
    collection_stage = user_collection['stage']
    if collection_stage == 'INITED':
        raise Exception("Unexpected stage 'INITED'. Aborting.")
    elif collection_stage == 'POPULATED':
        # TODO: in the future redo the pre-tagging of resources
        # TODO: when those have just been updated
        user_info = json.loads(session['current_guest'])
        request_info = dict()
        request_info[TWITTER] = user_info['apis']['twitter']
        request_info[COLLECTION_ID] = collection_id
        request_info[REQUEST_TYPE]=PRE_TAGGING_REQUEST_TYPE
        request_info[DATASET_SPECS] = user_collection[DATASET_SPECS];

        request_async_worker_job(request_info)

        # TODO: inform the client that there's nothing to show and
        # TODO: that it should listen to asynchronous events for when
        # TODO: the PRE_TAGGING phase is complete
        return dict()
    else:
        return dumps(user_collection["usls"])

def createCollectionDraft(collectionParams):
    client = MongoClient()
    library_db = client.library
    screen_name = get_screen_name()
    user_collections = library_db[screen_name+"_collections"]

    # reuse non-published collection that uses the same dataset
    user_collection = user_collections.find_one({"$and":[
        {DATASET_SPECS: {"source": collectionParams["dataset_source"]}},
        {"$or" : [
            {"stage": "INITED"},
            {"stage": "POPULATED"},
            {"stage": "DRAFT"}
        ]}
    ]})

    dataset_specs = {
        "source": collectionParams["dataset_source"]
    }

    if user_collection is None:
        iso_time = datetime.datetime.utcnow().isoformat()
        user_collection = {
            DATASET_SPECS: dataset_specs,
            "stage": "INITED",
            "created": iso_time
        }
        result = user_collections.insert_one(user_collection)

        collection_id = str(result.inserted_id)
    else:
        collection_id = str(user_collection["_id"])

    # populate the collection if it was just created
    # TODO: in the future, update the collection
    # TODO: at user-specified time period boundaries (day/week/month)
    if user_collection["stage"]=="INITED":
        user_info = json.loads(session['current_guest'])
        request_info = dict()
        request_info[TWITTER] = user_info['apis']['twitter']
        request_info[COLLECTION_ID] = collection_id
        request_info[REQUEST_TYPE]=DATASET_UPDATE_REQUEST_TYPE
        request_info[DATASET_SPECS] = dataset_specs

        request_async_worker_job(request_info)
    else:
        # immediately tell the client that we're good proceeding to the next stage
        push_server_event(screen_name, {
            REQUEST_TYPE: DATASET_UPDATE_REQUEST_TYPE,
            COLLECTION_ID: collection_id,
            MESSAGE: "Done",
            PROGRESS_STAGE: "DONE"
        })

    collectionParams["id"] = collection_id

    return collectionParams

def request_async_worker_job(request_info):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            RABBITMQ_HOST))
    channel = connection.channel()

    channel.basic_publish(exchange='async-workers-exchange',
                          routing_key='async-workers',
                          body=JSONEncoder().encode(request_info))
