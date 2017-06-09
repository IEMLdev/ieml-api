$(function() {
    var API_ROOT = 'http://127.0.0.1:8000/collections/';
    var api = API(API_ROOT);

    var collections = {};
    var documents = {};
    
    function formatDate(date) {
        var dt = date.split('T');
        var time = dt[1].split('.');

        return dt[0] + ' ' + time[0];
    }

    function authorsToStr(authors) {
        return authors.join(', ');
    }

    function authorsToArray(authors) {
        var array = authors.split(',').map(function(s) { return s.trim(); });
        // If authors is an empty string, array == [''], but we want []
        return !array[0] ? [] : array;
    }

    function tagsToArray(tags) {
        return authorsToArray(tags);
    }

    function unlinkedDocuments(collection) {
        var docs = [];

        for(let id in documents) {
            if(collection.documents.indexOf(id) == -1) {
                docs.push(id);
            }
        }

        return docs;
    }

    function renderCollectionList() {
        var list = $('#collection-list');
        list.empty();
        
        var li, a, collection;

        for(let collectionId in collections) {
            collection = collections[collectionId];

            li = document.createElement('li');
            a = document.createElement('a');
            a.setAttribute('data-id', collection.id);
            a.setAttribute('href', '');
            a.innerHTML = collection.title;

            $(a).click(function(e) {
                e.preventDefault();

                var id = $(this).data('id');
                renderCollection(collections[id]);
            });
            li.appendChild(a);

            list.append(li);
        }
    }

    function removeDocument(docId, collection) {
        var index = collection.documents.indexOf(docId);
        if(index != -1) {
            collection.documents.splice(index, 1);
        }

        api.updateCollection(
            collection,
            function(data) {
                collections[data.id] = data;
                renderDocumentList(data.documents);
                displayMessage('Document removed from collection successfully!');
            },
            function(err, details) {
                displayError('Unable to update collection: ' + err);
            }
        );
    }

    function renderDocumentList(docIds) {
        var li, a, doc;
        $('#collection-documents').empty();

        for(let docId of docIds) {
            doc = documents[docId];

            li = document.createElement('li');
            a = document.createElement('a');
            a.setAttribute('data-id', docId);
            a.setAttribute('href', '');
            a.innerHTML = doc.title;

            $(a).click(function(e) {
                e.preventDefault();
                var id = $(this).data('id');
                renderDocument(documents[id]);
            });
            li.appendChild(a);

            a = document.createElement('a');
            a.setAttribute('data-id', docId);
            a.setAttribute('href', '');
            a.setAttribute('class', 'remove');
            a.innerHTML = 'X';
            $(a).click(function(e) {
                e.preventDefault();
                var id = $(this).data('id');
                removeDocument(id, currentCollection());
            });
            li.appendChild(a);
            
            $('#collection-documents').append(li);
        }
    }

    function renderCollection(collection) {
        if(collection == null) return;

        $('#edit-collection-form input[name="title"]').val(collection.title);
        $('#edit-collection-form input[name="authors"]').val(authorsToStr(collection.authors));
        $('#collection-created-on span').html(formatDate(collection.created_on));
        $('#collection-updated-on span').html(formatDate(collection.updated_on));

        renderDocumentList(collection.documents);
        
        $('#document').hide();
        $('#add-document').hide();
        $('#collection').show();
        $('#collection').data('id', collection.id);
    }

    function renderDocument(doc) {
        var form = $('#edit-document-form');

        for(let key in doc) {
            form.find('*[name="' + key + '"]').val(doc[key]);
        }

        $('#document').show();
        $('#document').data('id', doc.id);
    }

    function renderLinkDocumentForm() {
        var docs = unlinkedDocuments(currentCollection());

        var select = $('#link-document-form select');
        select.empty();

        var option, doc;
        
        for(let docId of docs) {
            doc = documents[docId];

            option = document.createElement('option');
            option.setAttribute('value', doc.id);
            option.innerHTML = doc.title;

            select.append(option);
        }
    }

    function parseCollectionForm(form) {
        var data = {};

        data.title = form.find('*[name="title"]').val().trim();
        data.authors = authorsToArray(form.find('*[name="authors"]').val());

        return data;
    }

    function parseDocumentForm(form) {
        var data = {};
        
        data.title = form.find('*[name="title"]').val().trim();
        data.source = form.find('*[name="source"]').val().trim();
        data.authors = authorsToArray(form.find('*[name="authors"]').val());
        data.created_on = form.find('*[name="created_on"]').val();
        data.url = form.find('*[name="url"]').val();
        data.usl = form.find('*[name="usl"]').val();
        data.description = form.find('*[name="description"]').val();
        data.tags = tagsToArray(form.find('*[name="tags"]').val());
        data.image = form.find('*[name="image"]').val();

        if(!data.created_on) data.created_on = null;
        if(!data.usl) data.usl = null;
        if(!data.image) data.image = null;

        return data;
    }
    
    function parseLinkDocumentForm(form) {
        var data = {};

        data.id = form.find('*[name="documents"]').val();

        return data;
    }


    function displayFormErrors(form, errors) {
        var errDiv;

        for(let fieldName in errors) {
            errDiv = form.find('*[name="' + fieldName + '"]').next('div');
            errDiv.html(errors[fieldName]);
        }
    }

    function displayMessage(msg) {
        $('#messages').html(msg);
    }

    displayError = displayMessage;

    function cleanMessages() {
        $('#messages').html('');
    }
    
    function cleanFormErrors(form) {
        form.find('.field-errors').html('');
    }

    function cleanFormFields(form) {
        form.find('input[type!="submit"], textarea').val('');
    }

    function cleanForm(form) {
        cleanFormFields(form);
        cleanFormErrors(form);
    }

    function currentCollection() {
        var id = $('#collection').data('id');
        return collections[id];
    }

    function currentDocument() {
        var id = $('#document').data('id');
        return documents[id];
    }

    $('form').submit(function(e) {
        cleanFormErrors($(this));
        cleanMessages();
    });

    $('#create-collection form').submit(function(e) {
        e.preventDefault();
        var form = $(this);

        api.createCollection(
            parseCollectionForm(form),
            function(data) {
                collections[data.id] = data;
                cleanForm(form);
                $('#create-collection').hide();

                renderCollection(data);
                renderCollectionList();
                displayMessage('Collection created successfully!');
            },
            function(err, details) {
                displayError('Unable to create collection: ' + err);
                displayFormErrors(form, details);
            }
        );
    });
    
    $('#edit-collection-form').submit(function(e) {
        e.preventDefault();
        var form = $(this);

        var data = parseCollectionForm(form);
        data.id = $('#collection').data('id');

        api.updateCollection(
            data,
            function(data) {
                collections[data.id] = data;
                renderCollectionList();
                renderCollection(data);
                displayMessage('Collection updated successfully!');
            },
            function(err, details) {
                displayError('Unable to update collection: ' + err);
                displayFormErrors(form, details);
            }
        );
    });

    $('#create-document-form').submit(function(e) {
        e.preventDefault();
        var form = $(this);

        form.find('.field-errors').html('');

        api.createDocument(
            parseDocumentForm(form),
            currentCollection(),
            function(doc, collection) {
                collections[collection.id] = collection;
                documents[doc.id] = doc;
                renderDocumentList(collection.documents);
                cleanForm(form);
                displayMessage('Document created successfully!');
                $('#add-document').hide();
            },
            function(err, details) {
                displayError('Unable to create document: ' + err);
                displayFormErrors(form, details);
            }
        );
    });
    
    $('#link-document-form').submit(function(e) {
        e.preventDefault();

        var form = $(this);
        var data = parseLinkDocumentForm(form);

        currentCollection().documents.push(data.id);

        api.updateCollection(
            currentCollection(),
            function(data) {
                collections[data.id] = data; 
                cleanForm(form);
                renderDocumentList(currentCollection().documents);
                displayMessage('Document linked successfully!');
                $('#add-document').hide();
            }, function(err, details) {
                displayError('Unable to link document: ' + err);
                displayFormErrors(form, details);
            }
        );
    });
    
    $('#edit-document-form').submit(function(e) {
        e.preventDefault();

        var form = $(this);
        var data = parseDocumentForm(form);
        data.id = $('#document').data('id');

        api.updateDocument(data, function(data) {
            documents[data.id] = data; 
            cleanForm(form);
            renderDocumentList(currentCollection().documents);
            renderDocument(data);
            displayMessage('Document updated successfully!');
        }, function(err, details) {
            displayError('Unable to update document: ' + err);
            displayFormErrors(form, details);
        });
    });

    $('#add-collection-button').click(function(e) {
        $('#create-collection').toggle();
    });

    $('#add-document-button').click(function(e) {
        renderLinkDocumentForm();
        $('#add-document').toggle();
    });

    api.listCollections(function(data) {
        for(let col of data) {
            collections[col.id] = col;
        }
        renderCollectionList();

        $('#messages').html('');
        $('#sidebar').css('display', 'inline-block');
        $('#main').css('display', 'inline-block');
    }, function(err) {
        displayError('Unable to load collections: ' + err); 
    });
    
    api.listDocuments(function(data) {
        for(let doc of data) {
            documents[doc.id] = doc;
        }
    }, function(err) {
        displayError('Unable to load documents: ' + err); 
    });

});
