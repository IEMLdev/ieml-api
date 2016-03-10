#!/usr/bin/env mongo
var db = new Mongo().getDB("ieml_db");
db.dropDatabase();