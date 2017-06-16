var API = function(API_ROOT) {
    var module = {},
        cache = {
            'collections': null,
            'documents': null,
            'sources': null,
            'source_drivers': null,
            'tags': null
        };
    
    function cacheBuilderFactory(lookupField) {
        return function cacheBuilder(data) {
            var cache = {};

            for(let el of data) {
                cache[el[lookupField]] = el;
            }

            return cache;
        }
    }

    function list(name, cacheBuilder) {
        return function(success, error) {
            if (cache[name] != null) {
                return success(cache[name]);
            }

            $.ajax({
                url: API_ROOT + name + '/',
            })
            .done(function(data) {
                cache[name] = cacheBuilder(data); 
                success(cache[name]);
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                error(errorThrown, JSON.parse(jqXHR.responseText));
            });
        };
    }

    module.listCollections = list('collections', cacheBuilderFactory('id'));
    module.listDocuments = list('documents', cacheBuilderFactory('id'));
    module.listSources = list('sources', cacheBuilderFactory('id'));
    module.listSourceDrivers = list('source_drivers', cacheBuilderFactory('id'));
    module.listTags = list('tags', cacheBuilderFactory('text'));

    function get(listFunction) {
        return function(id, success, error) {
            listFunction(function(data) {
                success(data[id]);
            }, error);
        };
    }

    module.getCollection = get(module.listCollections);
    module.getDocument = get(module.listDocuments);
    module.getSource = get(module.listSources);
    module.getSourceDriver = get(module.listSourceDrivers);
    module.getTag = get(module.listTags);

    function insert(name, lookupField, create) {
        return function(obj, success, error) {
            var url = API_ROOT + name + '/';
            if(!create)
                url += obj.id + '/';

            $.ajax({
                url: url,
                method: create ? 'POST' : 'PUT',
                data: JSON.stringify(obj),
                contentType: 'application/json'
            })
            .done(function(data) {
                cache[name][data[lookupField]] = data;
                success(data);
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                error(errorThrown, JSON.parse(jqXHR.responseText));
            });
        };
    }
    
    function insertPost(create) {
        return function(obj, collection, success, error) {
            var url = API_ROOT + 'collections/' + collection.id + '/posts/';
            if(!create)
                url += obj.document + '/';

            $.ajax({
                url: url,
                method: create ? 'POST' : 'PUT',
                data: JSON.stringify(obj),
                contentType: 'application/json'
            })
            .done(function(data) {
                cache['collections'][collection.id].posts[data.document] = data;
                success(cache['collections'][collection.id]);
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                error(errorThrown, JSON.parse(jqXHR.responseText));
            });
        };
    }

    module.createCollection = insert('collections', 'id', true);
    module.createDocument = insert('documents', 'id', true);
    module.createTag = insert('tags', 'text', true);
    module.createPost = insertPost(true);

    // TODO
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

    module.updateCollection = insert('collections', 'id', false);
    module.updateDocument = insert('documents', 'id', false);
    module.updateTag = insert('tags', 'text', false);
    module.updatePost = insertPost(false);

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
            .done(function(resp) {
                delete cache[name][id];
                success(resp);
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                error(errorThrown, JSON.parse(jqXHR.responseText));
            });
        };
    }

    module.deleteTag = delete_('tags');

    return module;
};
