# First deployment

**Development mode only!**

* Install MongoDB **3.2** (can be done simply with Docker)
* Clone this repo
* Better: create a Python virtualenv, for instance with `pew`
* Install the dependencies: `pip install -r requirements.txt`
* `cd intlekt/django/intlekt`
* Edit `intlekt/settings.py`: set `ALLOWED_HOSTS` to `['*']`
* Create Mongo database: `mongo` then `use ieml`

# Update the repo

* `git stash`
* `git pull`
* `git stash apply`
* Clean the database: `mongo`
    * `use ieml`
    * `show collections`
    * For each collection `c`: `db.c.drop()`

# Run

* Start Mongo daemon
* Run the server (better: in the virtualenv created previously): `python3 manage.py runserver 0.0.0.0:8000`
