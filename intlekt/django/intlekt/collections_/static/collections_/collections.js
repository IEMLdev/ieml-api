$(function() {
    var API_ROOT = 'http://127.0.0.1:8000/collections/';
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

    function showCollection(collection) {
        $('#edit-collection-form input[name="title"]').val(collection.title);
        $('#edit-collection-form input[name="authors"]').val(authorsToStr(collection.authors));
        $('#collection-created-on span').html(collection.created_on);
        $('#collection-updated-on span').html(collection.updated_on);

        $('#collection').show();
        $('#collection').data('id', collection.id);
    }

    function writeCollectionToList(collection) {
        var li = $('#collections ul li[data-id="' + collection.id + '"]');
        var html = collection.title;

        if(li.length) {
            li.get(0).innerHTML = html;
            return;
        }

        li = document.createElement('li');
        li.setAttribute('data-id', collection.id);
        li.innerHTML = html;

        $(li).click(function() {
            var id = $(this).data('id');
            $.ajax({
                url: API_ROOT + 'collections/' + id + '/',
            })
            .done(function(data) {
                currentCollection = data;
                showCollection(data);
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                $('#messages').html('Unable to read collection, sorry. Message: ' + jqXHR.responseText);
            });
        });

        $('#collections ul').append(li);
    }

    function writeCollection(data, id) {
        id = (id == null) ? '' : id;
        data.updated_on = null; // For Python to store the current date

        $.ajax({
            url: API_ROOT + 'collections/' + id + (id ? '/' : ''),
            method: id ? 'PUT' : 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json'
        })
        .done(function(data) {
            writeCollectionToList(data);
            showCollection(data);
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            $('#messages').html('Unable to create collection, sorry. Message: ' + jqXHR.responseText);
        });
    }
    
    function writeDocument(data, id, collectionId) {
        id = (id == null) ? '' : id;

        $.ajax({
            url: API_ROOT + 'documents/' + id + (id ? '/' : ''),
            method: id ? 'PUT' : 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json'
        })
        .done(function(data) {
            if(currentCollection.documents.indexOf(data.id) == -1) {
                currentCollection.documents.push(data.id);
            }
            writeCollection(currentCollection, currentCollection.id);
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            $('#messages').html('Unable to create document, sorry. Message: ' + jqXHR.responseText);
        });
    }

    // Events

    var createCollectionForm = $('#create-collection form');
    createCollectionForm.submit(function(e) {
        e.preventDefault();
        var data = {};

        data.title = createCollectionForm.find('input[name="title"]').val().trim();
        data.authors = authorsToArray(createCollectionForm.find('input[name="authors"]').val());

        writeCollection(data, null);
    });

    var editCollectionForm = $('#edit-collection-form');
    editCollectionForm.submit(function(e) {
        e.preventDefault();
        var data = {};
    
        data.title = editCollectionForm.find('input[name="title"]').val().trim();
        data.authors = authorsToArray(editCollectionForm.find('input[name="authors"]').val());
        
        writeCollection(data, $('#collection').data('id'));
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

        writeDocument(data, null, $('#collection').data('id'));
    });

    // Init

    $.ajax({
        url: API_ROOT + 'collections/',
    })
    .done(function(data) {
        for(var i in data) {
            writeCollectionToList(data[i]);
        }
        $('#messages').html('');
        $('#main').show();
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        $('#messages').html('Unable to load collections, sorry. Message: ' + errorThrown);
    });
});
