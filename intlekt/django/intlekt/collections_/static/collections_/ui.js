$(function() {
    var API_ROOT = 'http://127.0.0.1:8000/collections/';
    var api = API(API_ROOT);

    var collections = {};
    var documents = {};
    var currentCollection = null;
    
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

    function renderCollectionList() {
        var list = $('#collection-list');
        list.empty();
        
        var li, collection;

        for(let collectionId in collections) {
            collection = collections[collectionId];

            li = document.createElement('li');
            li.setAttribute('data-id', collection.id);
            li.innerHTML = collection.title;

            $(li).click(function() {
                var id = $(this).data('id');
                renderCollection(collections[id]);
            });

            list.append(li);
        }
    }

    function renderDocumentList(docIds) {
        var li, doc;
        $('#collection-documents').empty();

        for(let docId of docIds) {
            doc = documents[docId];

            li = document.createElement('li');
            li.setAttribute('data-id', docId);
            li.innerHTML = doc.title;

            $(li).click(function() {
                var id = $(this).data('id');
                renderDocument(documents[id]);
            });

            $('#collection-documents').append(li);
        }
    }

    function renderCollection(collection) {
        currentCollection = collection;

        if(collection == null) return;

        $('#edit-collection-form input[name="title"]').val(collection.title);
        $('#edit-collection-form input[name="authors"]').val(authorsToStr(collection.authors));
        $('#collection-created-on span').html(formatDate(collection.created_on));
        $('#collection-updated-on span').html(formatDate(collection.updated_on));

        renderDocumentList(collection.documents);
        
        $('#document').hide();
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

    function collectionUpdated() {
        renderCollectionList();
        renderCollection(currentCollection);
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

    $('form').submit(function(e) {
        cleanFormErrors($(this));
        cleanMessages();
    });

    var createCollectionForm = $('#create-collection form');
    createCollectionForm.submit(function(e) {
        e.preventDefault();
        var data = {};

        data.title = createCollectionForm.find('input[name="title"]').val().trim();
        data.authors = authorsToArray(createCollectionForm.find('input[name="authors"]').val());

        api.createCollection(data, function(data) {
            collections.push(data);
            currentCollection = data;
            cleanFormFields(createCollectionForm);

            collectionUpdated();
        }, function(err, details) {
            displayError('Unable to create collection: ' + err);
            displayFormErrors(createCollectionForm, details);
        });
    });
    
    var editCollectionForm = $('#edit-collection-form');
    editCollectionForm.submit(function(e) {
        e.preventDefault();
        var data = {};
    
        data.id = currentCollection.id;
        data.title = editCollectionForm.find('input[name="title"]').val().trim();
        data.authors = authorsToArray(editCollectionForm.find('input[name="authors"]').val());

        api.updateCollection(data, function(data) {
            var collection;

            for(let i in collections) {
                collection = collections[i];
                if(collection.id == data.id) {
                    collections[i] = data;
                    currentCollection = data;
                    break;
                }
            }

            collectionUpdated();
            cleanFormFields(editCollectionForm);
            displayMessage('Collection updated successfully!');
        }, function(err, details) {
            displayError('Unable to update collection: ' + err);
            displayFormErrors(editCollectionForm, details);
        });
    });

    var createDocumentForm = $('#create-document-form');
    createDocumentForm.submit(function(e) {
        e.preventDefault();
        var data = {};

        data.title = createDocumentForm.find('*[name="title"]').val().trim();
        data.source = createDocumentForm.find('*[name="source"]').val().trim();
        data.authors = authorsToArray(createDocumentForm.find('*[name="authors"]').val());
        data.created_on = createDocumentForm.find('*[name="created_on"]').val();
        data.url = createDocumentForm.find('*[name="url"]').val();
        data.usl = createDocumentForm.find('*[name="usl"]').val();
        data.description = createDocumentForm.find('*[name="description"]').val();
        data.tags = tagsToArray(createDocumentForm.find('*[name="tags"]').val());
        data.image = createDocumentForm.find('*[name="image"]').val();

        if(!data.created_on) data.created_on = null;
        if(!data.usl) data.usl = null;
        if(!data.image) data.image = null;

        createCollectionForm.find('.field-errors').html('');

        api.createDocument(data, currentCollection, function(doc) {
            currentCollection.documents.push(doc.id);
            documents[doc.id] = doc;
            collectionUpdated();
            cleanFormFields(createDocumentForm);
        }, function(err, details) {
            displayError('Unable to create document: ' + err);
            displayFormErrors(createDocumentForm, details);
        });
    });
    
    var editDocumentForm = $('#edit-document-form');
    editDocumentForm.submit(function(e) {
        e.preventDefault();
        var data = {};
    
        data.id = $('#document').data('id');
        data.title = editDocumentForm.find('*[name="title"]').val().trim();
        data.source = editDocumentForm.find('*[name="source"]').val().trim();
        data.authors = authorsToArray(editDocumentForm.find('*[name="authors"]').val());
        data.created_on = editDocumentForm.find('*[name="created_on"]').val().trim();
        data.url = editDocumentForm.find('*[name="url"]').val().trim();
        data.usl = editDocumentForm.find('*[name="usl"]').val().trim();
        data.description = editDocumentForm.find('*[name="description"]').val().trim();
        data.tags = tagsToArray(editDocumentForm.find('*[name="tags"]').val());
        data.image = editDocumentForm.find('*[name="image"]').val().trim();

        if(!data.created_on) data.created_on = null;
        if(!data.usl) data.usl = null;
        if(!data.image) data.image = null;

        api.updateDocument(data, function(data) {
            var doc;

            for(let docId in documents) {
                doc = documents[docId];
                if(doc.id == data.id) {
                    documents[docId] = data;
                    break;
                }
            }

            renderDocument(data);
            displayMessage('Document updated successfully!');
        }, function(err, details) {
            displayError('Unable to update document: ' + err);
            displayFormErrors(editDocumentForm, details);
        });
    });

    $('#add-collection-button').click(function(e) {
        $('#create-collection').toggle();
    });

    $('#add-document-button').click(function(e) {
        $('#create-document-form').toggle();
    });

    api.listCollections(function(data) {
        for(let col of data) {
            collections[col.id] = col;
        }
        collectionUpdated();

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
