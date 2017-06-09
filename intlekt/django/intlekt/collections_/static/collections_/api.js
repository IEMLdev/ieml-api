var API = function(API_ROOT) {
    var module = {};

    function list(name) {
        return function(success, error) {
            $.ajax({
                url: API_ROOT + name + '/',
            })
            .done(success)
            .fail(function(jqXHR, textStatus, errorThrown) {
                error(errorThrown, JSON.parse(jqXHR.responseText));
            });
        };
    }

    module.listCollections = list('collections');
    module.listDocuments = list('documents');

    function get(name) {
        return function(id, success, error) {
            $.ajax({
                url: API_ROOT + name + '/' + id + '/',
            })
            .done(success)
            .fail(function(jqXHR, textStatus, errorThrown) {
                error(errorThrown, JSON.parse(jqXHR.responseText));
            });
        };
    }

    module.getCollection = get('collections');
    module.getDocument = get('documents');

    function create(name) {
        return function(obj, success, error) {
            $.ajax({
                url: API_ROOT + name + '/',
                method: 'POST',
                data: JSON.stringify(obj),
                contentType: 'application/json'
            })
            .done(success)
            .fail(function(jqXHR, textStatus, errorThrown) {
                error(errorThrown, JSON.parse(jqXHR.responseText));
            });
        };
    }

    module.createCollection = create('collections');
    module.createDocument = function(doc, collection, success, error) {
        $.ajax({
            url: API_ROOT + 'documents/',
            method: 'POST',
            data: JSON.stringify(doc),
            contentType: 'application/json'
        })
        .done(function(doc) {
            module.updateCollection(collection, function(col) {
                success(doc);
            }, error);
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            error(errorThrown, JSON.parse(jqXHR.responseText));
        });
    };

    function update(name) {
        return function(obj, success, error) {
            $.ajax({
                url: API_ROOT + name + '/' + obj.id + '/',
                method: 'PUT',
                data: JSON.stringify(obj),
                contentType: 'application/json'
            })
            .done(success)
            .fail(function(jqXHR, textStatus, errorThrown) {
                error(errorThrown, JSON.parse(jqXHR.responseText));
            });
        };
    }
    
    module.updateCollection = update('collections');
    module.updateDocument = update('documents');

    return module;
};
