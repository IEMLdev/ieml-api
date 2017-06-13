$(function() {
    var API_ROOT = 'http://127.0.0.1:8000/collections/';
    var SCOOPIT_DRIVER_ID = '593ef18cb15ab3332c49c945';
    var api = API(API_ROOT);

    var collections = {};
    var documents = {};
    var sources = {};
    var sourceDrivers = {};
    
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

    function collectedSourceToStr(collectedSource) {
        var driver = sourceDrivers[collectedSource.driver];
        var source = sources[driver.source];

        var str = source.name + ' (';

        if (driver.id == SCOOPIT_DRIVER_ID) {
            if (collectedSource.params.url != undefined)
                str += collectedSource.params.url;
            else if (collectedSource.params.user != undefined)
                str += collectedSource.params.user;
        }

        str += ')';

        return str;
    }

    function unlinkedDocuments(collection) {
        var docs = Object.keys(documents);
        var index;

        for(let doc in collection.documents) {
            index = docs.indexOf(doc);
            docs.splice(index, 1);
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

    function toggleDocumentVisibility(id, collection, visible) {
        collection.documents[id].hidden = !visible;

        api.updateCollection(
            collection,
            function(data) {
                collections[data.id] = data;
                renderDocumentList(data);
                if(visible) {
                    renderCollectedDocument(id, data);
                } else {
                    $('#document').hide();
                }
                displayMessage('Document removed from collection successfully!');
            },
            function(err, details) {
                displayError('Unable to update collection: ' + err);
            }
        );
    }

    function renderDocumentList(collection) {
        var li, a, span, collectedDoc;
        $('#collection-documents').empty();

        for(let docId in collection.documents) {
            collectedDoc = collection.documents[docId];

            li = document.createElement('li');

            if(!collectedDoc.hidden) {
                a = document.createElement('a');
                a.setAttribute('data-id', docId);
                a.setAttribute('href', '');
                a.innerHTML = documents[docId].title;
                $(a).click(function(e) {
                    e.preventDefault();
                    var id = $(this).data('id');
                    renderCollectedDocument(id, collection);
                });
                li.appendChild(a);

                a = document.createElement('a');
                a.setAttribute('data-id', docId);
                a.setAttribute('href', '');
                a.setAttribute('class', 'hide');
                a.innerHTML = 'hide';
                $(a).click(function(e) {
                    e.preventDefault();
                    var id = $(this).data('id');
                    toggleDocumentVisibility(id, currentCollection(), false);
                });
                li.appendChild(a);
            } else {
                span = document.createElement('span');
                span.innerHTML = documents[docId].title + ' ';
                li.appendChild(span);
                
                a = document.createElement('a');
                a.setAttribute('data-id', docId);
                a.setAttribute('href', '');
                a.setAttribute('class', 'show');
                a.innerHTML = 'show';
                $(a).click(function(e) {
                    e.preventDefault();
                    var id = $(this).data('id');
                    toggleDocumentVisibility(id, currentCollection(), true);
                });
                li.appendChild(a);
            }
            
            $('#collection-documents').append(li);
        }
    }
    
    function renderSourceList(collection) {
        var li, a, src;
        $('#collection-sources').empty();

        for(let i in collection.sources) {
            src = collection.sources[i];

            li = document.createElement('li');

            a = document.createElement('a');
            a.setAttribute('href', '');
            a.innerHTML = collectedSourceToStr(src);
            (function(i) {
                $(a).click(function(e) {
                    e.preventDefault();

                    api.requestSource(
                        collection,
                        sourceDrivers[collection.sources[i].driver],
                        collection.sources[i].params,
                        function(resp) {
                            displayMessage('Source being collected... Reload the page to see new documents.');
                        },
                        function(err, details) {
                            displayError('Unable to request source: ' + err);
                        }
                    );
                });
            })(i);
            li.appendChild(a);

            a = document.createElement('a');
            a.setAttribute('href', '');
            a.setAttribute('class', 'hide');
            a.innerHTML = 'X';
            (function(i) {
                $(a).click(function(e) {
                    e.preventDefault();

                    collection.sources.splice(i, 1);
                    api.updateCollection(
                        collection,
                        function(data) {
                            collections[data.id] = data;
                            renderSourceList(data);
                            displayMessage('Source unlinked successfully!');
                        },
                        function(err, details) {
                            displayError('Unable to unlink source: ' + err);
                            displayFormErrors(form, details);
                        }
                    );
                });
            })(i);
            li.appendChild(a);

            $('#collection-sources').append(li);
        }
    }

    function renderCollection(collection) {
        if(collection == null) return;

        $('#edit-collection-form input[name="title"]').val(collection.title);
        $('#edit-collection-form input[name="authors"]').val(authorsToStr(collection.authors));
        $('#collection-created-on span').html(collection.created_on);
        $('#collection-updated-on span').html(collection.updated_on);

        renderSourceList(collection);
        renderDocumentList(collection);
        
        $('#document').hide();
        $('#add-document').hide();
        $('#add-source').hide();
        $('#collection').show();
        $('#collection').data('id', collection.id);
    }

    function renderCollectedDocument(id, collection) {
        var form = $('#edit-document-form');
        var doc = collection.documents[id];

        for(let key in doc) {
            form.find('*[name="' + key + '"]').val(doc[key]);
        }
        form.find('*[name="url_collected"]').val(doc.url);

        $('#document').show();
        $('#document').data('id', id);
    }

    function renderCollectDocumentForm() {
        var docs = unlinkedDocuments(currentCollection());

        var select = $('#collect-document-form select');
        select.empty();

        var option, doc;
        
        option = document.createElement('option');
        option.setAttribute('value', '');
        select.append(option);

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

    function parseCollectedDocumentForm(form) {
        var collectedDoc = {};
        
        collectedDoc.collected_on = form.find('*[name="collected_on"]').val();
        collectedDoc.usl = form.find('*[name="usl"]').val();
        collectedDoc.url = form.find('*[name="url_collected"]').val();
        collectedDoc.tags = tagsToArray(form.find('*[name="tags"]').val());
        collectedDoc.image = form.find('*[name="image"]').val();
        collectedDoc.description = form.find('*[name="description"]').val();

        if(!collectedDoc.collected_on) delete collectedDoc.collected_on;
        if(!collectedDoc.usl) collectedDoc.usl = null;
        if(!collectedDoc.image) collectedDoc.image = null;
        if(!collectedDoc.url) collectedDoc.url = null;

        return collectedDoc;
    }

    function parseCollectDocumentForm(form) {
        var doc = {};
        
        doc.id = form.find('*[name="documents"]').val();
        doc.title = form.find('*[name="title"]').val().trim();
        doc.authors = authorsToArray(form.find('*[name="authors"]').val());
        doc.created_on = form.find('*[name="created_on"]').val();
        doc.url = form.find('*[name="url"]').val();

        if(!doc.created_on) doc.created_on = null;

        return {
            doc: doc,
            collectedDoc: parseCollectedDocumentForm(form)
        };
    }

    function parseAddScoopitByUrlForm(form) {
        var params = {};

        params.url = form.find('*[name="url"]').val();

        return params;
    }
    
    function parseAddScoopitByUserForm(form) {
        var params = {};

        params.user = form.find('*[name="user"]').val();

        return params;
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

    $('#collect-document-form').submit(function(e) {
        e.preventDefault();
        var form = $(this);

        cleanFormErrors(form);
        var parsedForm = parseCollectDocumentForm(form);
        var doc = parsedForm.doc;
        var collectedDoc = parsedForm.collectedDoc;

        function createDocumentCallback(doc) {
            documents[doc.id] = doc;

            var col = currentCollection();
            col.documents[doc.id] = collectedDoc;


            api.updateCollection(
                col,
                function(collection) {
                    collections[collection.id] = collection;

                    renderDocumentList(collection);
                    renderCollectedDocument(doc.id, collection);
                    cleanForm(form);
                    displayMessage('Document collected successfully!');
                    $('#collect-document').hide();
                },
                function(err, details) {
                    displayError('Unable to create document: ' + err);
                    displayFormErrors(form, details);
                }
            );
        }

        if(doc.id != '') {
            createDocumentCallback(documents[doc.id]);
        }
        else {
            api.createDocument(
                doc,
                createDocumentCallback,
                function(err, details) {
                    displayError('Unable to create document: ' + err);
                    displayFormErrors(form, details);
                }
            );
        }
    });
    
    $('#edit-document-form').submit(function(e) {
        e.preventDefault();

        var form = $(this);
        var data = parseCollectedDocumentForm(form);
        var id = $('#document').data('id');
        var col = currentCollection();

        col.documents[id] = data;

        api.updateCollection(col, function(collection) {
            collections[collection.id] = collection; 
            cleanForm(form);
            renderCollectedDocument(id, collection);
            displayMessage('Document updated successfully!');
        }, function(err, details) {
            displayError('Unable to update document: ' + err);
            displayFormErrors(form, details);
        });
    });

    $('#add-collection-button').click(function(e) {
        $('#create-collection').toggle();
    });

    $('#add-source-button').click(function(e) {
        $('#add-source').toggle();
    });

    $('#collect-document-button').click(function(e) {
        renderCollectDocumentForm();
        $('#collect-document').toggle();
    });

    function addSourceFactory(form, driver, parser) {
        form.submit(function(e) {
            e.preventDefault();

            var col = currentCollection();
            var source = {
                driver: driver,
                params: parser(form) 
            };
            col.sources.push(source);

            api.updateCollection(col, function(collection) {
                collections[collection.id] = collection; 
                cleanForm(form);
                renderSourceList(collection);
                displayMessage('Source added successfully!');
            }, function(err, details) {
                displayError('Unable to add source: ' + err);
                displayFormErrors(form, details);
            });
        });
    }

    addSourceFactory(
        $('#add-scoopit-url-source-form'),
        SCOOPIT_DRIVER_ID,
        parseAddScoopitByUrlForm
    );

    addSourceFactory(
        $('#add-scoopit-user-source-form'),
        SCOOPIT_DRIVER_ID,
        parseAddScoopitByUserForm
    );

    // Init

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
    
    api.listSources(function(data) {
        for(let obj of data) {
            sources[obj.id] = obj;
        }
    }, function(err) {
        displayError('Unable to load sources: ' + err); 
    });
    
    api.listSourceDrivers(function(data) {
        for(let obj of data) {
            sourceDrivers[obj.id] = obj;
        }
    }, function(err) {
        displayError('Unable to load source drivers: ' + err); 
    });
});
