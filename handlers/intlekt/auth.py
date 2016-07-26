from flask import redirect
from flask import session
import json

def logout():
    origin = session["origin"];
    session.clear();
    return redirect(origin + "/login", 302)

def info():
    current_guest_json = session.get("current_guest")
    print(current_guest_json)
    current_guest = json.loads(current_guest_json)
    print(current_guest)
    return {
        'since' : current_guest['since'],
        'screen_name': current_guest['apis']['twitter']['screen_name'],
        'access_token': current_guest['apis']['twitter']['access_token']
    }