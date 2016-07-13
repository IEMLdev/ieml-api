# Dictionary REST API test design

The purpose of this document is to give design ideas for the test suit that will be implemented to test the API.
Tests that verify the correctness of the underlying algorithms have already been implemented.

The main goal here is to test the functionality of the public API endpoints.

The main goal here is to test the functionality of the public API endpoints.

## Description of the API endoints

### Creation, deletion and listing of IEML terms from the dictionary

These operations are done by the following API endpoints:

#### Creation:

#### Deletion:

#### Check Existence:

```
GET dictionary.ieml.io/api/exists/ieml/[ieml-term]
```

Where [ieml-term] is the ieml term for which we want to verify the existance in the database.

#### Listing all the terms:

```
GET dictionary.ieml.io/api/allieml
```

This endpoint returns a list of all IEML terms that are available in the database. The list is a list of term objects (see API docs for the structure of the term object).

### Obtaining paradigm table related to an IEML term

```
POST parser.ieml.io/rest/iemlparser/tables
```

Sent with a query string:

```
iemltext=[IEML-term]
```

### Operations related to relations between IEML terms

#### Obtain the relations for an IEML term:

```
POST dictionary.ieml.io/api/rels
```

We send this HTTP request with a payload such as this:

```
{
    ieml: "[ieml-term]"
}
```

This will return a list of relations for [ieml-term]. The relations objects have the following structure:

```
{
    rellist: [list of ieml terms that are related to [ieml-term]]
    reltype: "Type of relation"
    visible: Boolean. Tells us if the relation should visible or not.
}
```

### Deprecated endpoints

#### Get the descendance tree of an IEML term

```
POST parser.ieml.io/rest/iemlparser/tree
```

With the query string:

```
iemltext=[IEML-term]
```

#### Get annotations

```
POST dictionary.ieml.io/api/getannotations
```

With the payload:

```
{ieml: "[IEML-term]]"}
```

## Testing senarios

A potential sequence for testing the API would be the following:

1. Create a basic IEML term
2. Create another IEML term, tag it as a paradigm and inhibt some relations
3. Check the existence of both terms created in **(1)** and **(2)** using the `api/exists/ieml/[ieml-term]` endpoint
4. Get a list of all IEML terms using `dictionary.ieml.io/api/allieml` and verify that both terms created in **(1)** and **(2)** are present

  1. Verify that the term created in **(2)** is, in fact, a paradigm
  2. Verify that the inhibited relations in **(2)** have their visibility set to `False` using `dictionary.ieml.io/api/rels`

5. Check that the paradigm created in **(2)** has a table by using the `parser.ieml.io/rest/iemlparser/tables` endpoint

6. Delete both terms in **(1)** and **(2)**, check that they don't exist anymore and verify that they're not found when using `dictionary.ieml.io/api/allieml`
