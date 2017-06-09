var API = function(API_ROOT) {
    var module = {};

    module.listCollections = function(success, error) {
        $.ajax({
            url: API_ROOT + 'collections/',
        })
        .done(success)
        .fail(function(jqXHR, textStatus, errorThrown) {
            error(errorThrown, JSON.parse(jqXHR.responseText));
        });
    };

    module.getCollection = function(id, success, error) {
        $.ajax({
            url: API_ROOT + 'collections/' + id + '/',
        })
        .done(success)
        .fail(function(jqXHR, textStatus, errorThrown) {
            error(errorThrown, JSON.parse(jqXHR.responseText));
        });
    };

    module.createCollection = function(collection, success, error) {
        $.ajax({
            url: API_ROOT + 'collections/',
            method: 'POST',
            data: JSON.stringify(collection),
            contentType: 'application/json'
        })
        .done(success)
        .fail(function(jqXHR, textStatus, errorThrown) {
            error(errorThrown, JSON.parse(jqXHR.responseText));
        });
    };
    
    module.updateCollection = function(collection, success, error) {
        $.ajax({
            url: API_ROOT + 'collections/' + collection.id + '/',
            method: 'PUT',
            data: JSON.stringify(collection),
            contentType: 'application/json'
        })
        .done(success)
        .fail(function(jqXHR, textStatus, errorThrown) {
            error(errorThrown, JSON.parse(jqXHR.responseText));
        });
    };

    module.listDocuments = function(success, error) {
        $.ajax({
            url: API_ROOT + 'documents/',
        })
        .done(success)
        .fail(function(jqXHR, textStatus, errorThrown) {
            error(errorThrown, JSON.parse(jqXHR.responseText));
        });
    };

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

    return module;
};
