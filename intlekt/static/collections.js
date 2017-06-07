$(function() {
    var API_ROOT = 'http://127.0.0.1:5000/';

    function displayCollection(collection) {
        $('#collections ul').append(
            '<li data-id="' + collection.id + '">' +
            collection.title +
            ' (' + collection.authors.join(', ') + ')' +
            '</li>'
        );
    }

    function createCollection(title, authors) {
        $.ajax({
            url: API_ROOT + 'collections/',
            method: 'POST',
            data: JSON.stringify({title: title, authors: authors}),
            contentType: 'application/json'
        })
        .done(function(data) {
            displayCollection(data);
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
        var authors = createCollectionForm.find('input[name="authors"]').val();
        authors = authors.split(',').map(function(s) { return s.trim(); });

        createCollection(title, authors);
    });

    // Init

    $.ajax({
        url: API_ROOT + 'collections/',
    })
    .done(function(data) {
        for(var i in data.data) {
            displayCollection(data.data[i]);
        }
        $('#messages').html('');
        $('#main').show();
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        $('#messages').html('Unable to load collections, sorry. Message: ' + errorThrown);
    });
});
