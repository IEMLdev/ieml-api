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
    }
)