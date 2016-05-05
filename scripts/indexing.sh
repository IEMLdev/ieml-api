#!/usr/bin/env mongo

db.terms.createIndex(
    {
        IEML: "text",
        FR: "text",
        EN: "text"
    }
)

db.propositions.createIndex({ "TAGS.FR" : 1 }, { unique: true })
db.propositions.createIndex({"TAGS.EN" : 1}, {unique: true})

db.texts.createIndex({ "TAGS.FR" : 1 }, { unique: true })
db.texts.createIndex({ "TAGS.EN" : 1 }, { unique: true })

db.hypertexts.createIndex({ "TAGS.FR" : 1 }, { unique: true })
db.hypertexts.createIndex({ "TAGS.EN" : 1 }, { unique: true })




