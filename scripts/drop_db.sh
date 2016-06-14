#!/usr/bin/env mongo
var current_db = new Mongo().getDB("ieml_db");
var old_db = new Mongo().getDB("old_db");
current_db.dropDatabase();
old_db.dropDatabase();