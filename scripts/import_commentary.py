import json
import base64
import ssl
from urllib.request import urlopen, Request

from ieml.dictionary.script.operator import script

TERM_API_COMMENTS = "https://dev.intlekt.io/iemlapi/terme_api.json"
RELATIONS_API_COMMENTS = "https://dev.intlekt.io/iemlapi/relations_api.json"



def download_comments_terms(username, password):
    userpass = '%s:%s' % (username, password)
    auth_encoded = base64.encodebytes(userpass.encode('ascii'))[:-1]

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = Request(TERM_API_COMMENTS)
    req.add_header('Authorization', "Basic YWRtaW46ZHJ1cGFscGxvdGlu")

    response = urlopen(req, context=ctx)
    str_response = response.read().decode('utf-8')
    j = json.loads(str_response)

    return {script(_t["IEML"]["value"]) : {
                            "comment": _t["commentaire_sur_terme"],
                            "drupal_nid": _t["Nid"]
    } for _t in j}

if __name__ == "__main__":
    t = download_comments_terms("admin", "drupalplotin")
    print(t)