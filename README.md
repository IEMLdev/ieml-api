# Setting up the RESTful API

Here's what you need to do to set up the API

## Dependencies

You'll need a mongodb 3.2 server running on your machine. 
On Ubuntu, use this tutorial to set it up: https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-ubuntu-14-04

Then, we'll need Python3 and the pip3 installer:

```bash
sudo apt-get install python3 python3-pip python3-numpy
```


Then, we'll install flask, pymongo and flask-restful :

```bash
sudo pip3 install pymongo flask flask-restful ply
```

## Setting up the DB

Be sure to be at the root of the project's folder, and run

```bash
bash scripts/reload_db.sh
```


## Launching the API on a local machine

Just run the app.py python script :

```bash
python3 app.py
```

## Needed special config to have the client and the API server work together

You'll need to configure NGINX to do some reverse-proxying. First, be sure to uninstall and/or stop Apache.
Then, run

```bash
sudo apt-get install nginx
sudo nano /etc/nginx/sites-available/ieml-propositions
```

Then paste the following code. Be sure to replace "PATH_TO_THE_CLONED_REPOS_FOLDER"
 by the absolute path to the repo's cloned folder.

```nginx
server {
    listen      3000;

    root "PATH_TO_THE_CLONED_REPOS_FOLDER/views";

    location / {
        try_files $uri /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
    }
}
```

Then, we'll need to softlink that config file to add it to the activated sites, and restart Nginx so it
takes the config into account. 

```bash
sudo ln -s /etc/nginx/sites-available/ieml-propositions /etc/nginx/sites-enabled/ieml-propositions
sudo service nginx restart
```

The client should be reachable on your machine at 127.0.0.1:3000/


## Reloading the database

Re-run the database setup script, it'll drop the old database automatically
