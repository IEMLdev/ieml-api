$(function() {
    var API_ROOT = 'http://127.0.0.1:5000/';

    function authorsToStr(authors) {
        return authors.join(', ');
    }

    function authorsToArray(authors) {
        return authors.split(',').map(function(s) { return s.trim(); });
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
                url: API_ROOT + 'collections/' + id,
            })
            .done(function(data) {
                showCollection(data);
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                $('#messages').html('Unable to read collection, sorry. Message: ' + jqXHR.responseText);
            });
        });

        $('#collections ul').append(li);
    }

    function writeCollection(id, title, authors) {
        id = (id == null) ? '' : id;

        $.ajax({
            url: API_ROOT + 'collections/' + id + '/',
            method: id ? 'PUT' : 'POST',
            data: JSON.stringify({title: title, authors: authors, updated_on: null}),
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

    // Events

    var createCollectionForm = $('#create-collection form');
    createCollectionForm.submit(function(e) {
        e.preventDefault();

        var title = createCollectionForm.find('input[name="title"]').val().trim();
        var authors = authorsToArray(createCollectionForm.find('input[name="authors"]').val());

        writeCollection(null, title, authors);
    });

    var editCollectionForm = $('#edit-collection-form');
    editCollectionForm.submit(function(e) {
        e.preventDefault();
    
        var title = editCollectionForm.find('input[name="title"]').val().trim();
        var authors = authorsToArray(editCollectionForm.find('input[name="authors"]').val());
        
        writeCollection($('#collection').data('id'), title, authors);
    });

    // Init

    $.ajax({
        url: API_ROOT + 'collections/',
    })
    .done(function(data) {
        for(var i in data.data) {
            writeCollectionToList(data.data[i]);
        }
        $('#messages').html('');
        $('#main').show();
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        $('#messages').html('Unable to load collections, sorry. Message: ' + errorThrown);
    });
});
