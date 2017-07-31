import json
import base64
import io
import ssl
from urllib.request import urlopen, Request
import os

import boto3

from ieml.dictionary.script.operator import script
from ieml.tools import list_bucket

TERM_API_COMMENTS = "https://dev.intlekt.io/iemlapi/terme_api.json"
RELATIONS_API_COMMENTS = "https://dev.intlekt.io/iemlapi/relations_api.json"

COMMENTARY_BUCKET = "https://s3.amazonaws.com/ieml-commentary"


def download_comments_terms(username, password):
    userpass = '%s:%s' % (username, password)
    auth_encoded = base64.encodebytes(userpass.encode('ascii'))[:-1]

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = Request(TERM_API_COMMENTS)
    req.add_header('Authorization', 'Basic %s' %  str(auth_encoded, 'utf-8'))

    response = urlopen(req, context=ctx)
    str_response = response.read().decode('utf-8')
    j = json.loads(str_response)

    return {str(script(_t["IEML"]["value"])) : {
                            "comment": _t["commentaire_sur_terme"],
                            "drupal_nid": _t["Nid"]
    } for _t in j}


def get_last_commentaries():
    entries = list_bucket(COMMENTARY_BUCKET)
    if not entries:
        raise ValueError("No comments entry in %s."%COMMENTARY_BUCKET)

    str_response = urlopen(os.path.join(COMMENTARY_BUCKET, entries[0])).read().decode('utf-8')
    return json.loads(str_response)


def save_comments_to_bucket(bucket_name, comments, filename):
    s3 = boto3.resource('s3')

    bucket_name = bucket_name.split('/')[-1]
    bucket = s3.Bucket(bucket_name)
    obj = bucket.Object(filename)
    obj.upload_fileobj(io.BytesIO(bytes(json.dumps(comments), 'utf-8')))
    obj.Acl().put(ACL='public-read')


if __name__ == "__main__":
    # t = download_comments_terms("admin", "drupalplotin")
    # save_comments_to_bucket(COMMENTARY_BUCKET, t, 'comments.json')
    print(get_last_commentaries())