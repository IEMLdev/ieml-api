#!/usr/bin/env mongo

db.terms.createIndex(
    {
        IEML: "text",
        FR: "text",
        EN: "text"
    }
)
db.propositions.createIndex(
    {
        IEML: "text",
        TAGS: "text",
        _id: "text"
    }
)
db.propositions.ensureIndex({"TAGS.FR" : 1})
db.propositions.ensureIndex({"TAGS.EN" : 1})

