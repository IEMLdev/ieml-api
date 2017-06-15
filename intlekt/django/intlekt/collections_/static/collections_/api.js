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
    module.listSources = list('sources');
    module.listSourceDrivers = list('source_drivers');
    module.listTags = list('tags');

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
    module.createDocument = create('documents');
    module.createTag = create('tags');
    module.createCollectedDocument = function(doc, collection, success, error) {
        $.ajax({
            url: API_ROOT + 'collections/' + collection.id + '/posts/',
            method: 'POST',
            data: JSON.stringify(doc),
            contentType: 'application/json'
        })
        .done(function(doc) {
            collection.documents.push(doc.id);

            module.updateCollection(collection, function(col) {
                success(doc, collection);
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
    module.updateTag = update('tags');

    module.requestSource = function(collection, driver, params, success, error) {
        params.collection_id = collection.id;

        $.ajax({
            url: driver.url,
            method: 'POST',
            data: JSON.stringify(params),
            contentType: 'application/json'
        })
        .done(success)
        .fail(function(jqXHR, textStatus, errorThrown) {
            error(errorThrown, JSON.parse(jqXHR.responseText));
        });
    };
    
    function delete_(name) {
        return function(id, success, error) {
            $.ajax({
                url: API_ROOT + name + '/' + id + '/',
                method: 'DELETE',
            })
            .done(success)
            .fail(function(jqXHR, textStatus, errorThrown) {
                error(errorThrown, JSON.parse(jqXHR.responseText));
            });
        };
    }

    module.deleteTag = delete_('tags');

    return module;
};
