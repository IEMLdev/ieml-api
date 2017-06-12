$(function() {
    var API_ROOT = 'http://127.0.0.1:8000/collections/';
    var api = API(API_ROOT);

    var collections = {};
    var documents = {};
    
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

    function unlinkedDocuments(collection) {
        var docs = Object.keys(documents);
        var index;

        for(let collectedDoc of collection.documents) {
            index = docs.indexOf(collectedDoc.document);
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

    function toggleDocumentVisibility(index, collection, visible) {
        collection.documents[index].hidden = !visible;

        api.updateCollection(
            collection,
            function(data) {
                collections[data.id] = data;
                renderDocumentList(data);
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

        for(let i in collection.documents) {
            collectedDoc = collection.documents[i];

            li = document.createElement('li');

            if(!collectedDoc.hidden) {
                a = document.createElement('a');
                a.setAttribute('data-index', i);
                a.setAttribute('href', '');
                a.innerHTML = documents[collectedDoc.document].title;
                $(a).click(function(e) {
                    e.preventDefault();
                    var i = $(this).data('index');
                    renderCollectedDocument(i, collection);
                });
                li.appendChild(a);

                a = document.createElement('a');
                a.setAttribute('data-index', i);
                a.setAttribute('href', '');
                a.setAttribute('class', 'hide');
                a.innerHTML = 'hide';
                $(a).click(function(e) {
                    e.preventDefault();
                    var index = $(this).data('index');
                    toggleDocumentVisibility(index, currentCollection(), false);
                });
                li.appendChild(a);
            } else {
                span = document.createElement('span');
                span.innerHTML = documents[collectedDoc.document].title + ' ';
                li.appendChild(span);
                
                a = document.createElement('a');
                a.setAttribute('data-index', i);
                a.setAttribute('href', '');
                a.setAttribute('class', 'show');
                a.innerHTML = 'show';
                $(a).click(function(e) {
                    e.preventDefault();
                    var index = $(this).data('index');
                    toggleDocumentVisibility(index, currentCollection(), true);
                });
                li.appendChild(a);
            }
            
            $('#collection-documents').append(li);
        }
    }

    function renderCollection(collection) {
        if(collection == null) return;

        $('#edit-collection-form input[name="title"]').val(collection.title);
        $('#edit-collection-form input[name="authors"]').val(authorsToStr(collection.authors));
        $('#collection-created-on span').html(formatDate(collection.created_on));
        $('#collection-updated-on span').html(formatDate(collection.updated_on));

        renderDocumentList(collection);
        
        $('#document').hide();
        $('#add-document').hide();
        $('#collection').show();
        $('#collection').data('id', collection.id);
    }

    function renderCollectedDocument(index, collection) {
        var form = $('#edit-document-form');
        var doc = collection.documents[index];

        for(let key in doc) {
            form.find('*[name="' + key + '"]').val(doc[key]);
        }

        $('#document').show();
        $('#document').data('index', index);
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
        collectedDoc.comments = form.find('*[name="comments"]').val();

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
        doc.description = form.find('*[name="description"]').val();

        if(!doc.created_on) doc.created_on = null;

        return {
            doc: doc,
            collectedDoc: parseCollectedDocumentForm(form)
        };
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
            collectedDoc.document = doc.id;

            var col = currentCollection();
            col.documents.push(collectedDoc);


            api.updateCollection(
                col,
                function(collection) {
                    collections[collection.id] = collection;

                    renderDocumentList(collection);
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
    
    $('#link-document-form').submit(function(e) {
        e.preventDefault();

        var form = $(this);
        var data = parseLinkDocumentForm(form);

        currentCollection().documents.push(data.id);

        api.updateCollection(
            currentCollection(),
            function(data) {
                collections[data.id] = data; 
                cleanForm(form);
                renderDocumentList(currentCollection());
                displayMessage('Document linked successfully!');
                $('#add-document').hide();
            }, function(err, details) {
                displayError('Unable to link document: ' + err);
                displayFormErrors(form, details);
            }
        );
    });
    
    $('#edit-document-form').submit(function(e) {
        e.preventDefault();

        var form = $(this);
        var data = parseCollectedDocumentForm(form);
        var index = $('#document').data('index');
        var col = currentCollection();

        data.document = col.documents[index].document;
        col.documents[index] = data;

        api.updateCollection(col, function(collection) {
            collections[collection.id] = collection; 
            cleanForm(form);
            renderCollectedDocument(index, collection);
            displayMessage('Document updated successfully!');
        }, function(err, details) {
            displayError('Unable to update document: ' + err);
            displayFormErrors(form, details);
        });
    });

    $('#add-collection-button').click(function(e) {
        $('#create-collection').toggle();
    });

    $('#collect-document-button').click(function(e) {
        renderCollectDocumentForm();
        $('#collect-document').toggle();
    });

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
});
