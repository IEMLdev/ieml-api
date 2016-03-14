#!/usr/bin/env mongo

db.terms.createIndex(
    {
        IEML: "text",
        FR: "text",
        EN: "text"
    }
)