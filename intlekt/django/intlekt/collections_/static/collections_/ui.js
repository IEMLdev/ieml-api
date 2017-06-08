$(function() {
    var API_ROOT = 'http://127.0.0.1:8000/collections/';
    var api = API(API_ROOT);

    var collections = [];
    var documents = [];
    var currentCollection = null;
    
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
        
        var li;

        for(let collection of collections) {
            li = document.createElement('li');
            li.setAttribute('data-id', collection.id);
            li.innerHTML = collection.title;

            $(li).click(function() {
                var id = $(this).data('id');

                api.getCollection(id, renderCollection, function(err) {
                    displayError('Unable to read collection: ' + err); 
                });
            });

            list.append(li);
        }
    }

    function renderCollection(collection) {
        currentCollection = collection;

        if(collection == null) return;

        $('#edit-collection-form input[name="title"]').val(collection.title);
        $('#edit-collection-form input[name="authors"]').val(authorsToStr(collection.authors));
        $('#collection-created-on span').html(collection.created_on);
        $('#collection-updated-on span').html(collection.updated_on);

        var li, id;
        $('#collection-documents').empty();

        for(var i in collection.documents) {
            id = collection.documents[i];

            li = document.createElement('li');
            li.setAttribute('data-id', id);
            li.innerHTML = id;
            
            $('#collection-documents').append(li);
        }

        $('#collection').show();
        $('#collection').data('id', collection.id);
    }

    function collectionUpdated() {
        renderCollectionList();
        renderCollection(currentCollection);
    }

    function displayMessage(msg) {
        $('#messages').html(msg);
    }

    displayError = displayMessage;
    
    var createCollectionForm = $('#create-collection form');
    createCollectionForm.submit(function(e) {
        e.preventDefault();
        var data = {};

        data.title = createCollectionForm.find('input[name="title"]').val().trim();
        data.authors = authorsToArray(createCollectionForm.find('input[name="authors"]').val());

        api.createCollection(data, function(data) {
            collections.push(data);
            currentCollection = data;

            collectionUpdated();
        }, function(err) {
            displayError('Unable to create collection: ' + err);
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
        }, function(err) {
            displayError('Unable to update collection: ' + err);
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


        api.createDocument(data, currentCollection, function(doc) {
            currentCollection.documents.push(doc.id);
            documents[doc.id] = doc;
            collectionUpdated();
        }, function(err) {
            displayError('Unable to create document: ' + err);
        });
    });


    api.listCollections(function(data) {
        collections = data;
        collectionUpdated();

        $('#messages').html('');
        $('#main').show();
    }, function(err) {
        displayError('Unable to load collections: ' + err); 
    });
});
