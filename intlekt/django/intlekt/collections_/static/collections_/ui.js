$(function() {
    
    // Globals
    
    var API_ROOT = 'http://127.0.0.1:8000/collections/';
    var SCOOPIT_DRIVER_ID = '593ef18cb15ab3332c49c945';
    var DEFAULT_DOCUMENT_TITLE = 'Unknown title';
    var api = API(API_ROOT);

    var currentCollection;

    // Helpers
    
    function listToStr(list) {
        return list.join(', ');
    }

    var authorsToStr = listToStr;
    var keywordsToStr = listToStr;

    function strToArray(str) {
        var array = str.split(',').map(function(s) { return s.trim(); });
        // If str is an empty string, array == [''], but we want []
        return !array[0] ? [] : array;
    }

    var authorsToArray = strToArray;
    var tagsToArray = strToArray;
    var keywordsToArray = strToArray;

    function collectedSourceToStr(collectedSource, callback) {
        api.getSourceDriver(
            collectedSource.driver,
            function(driver) {
                api.getSource(
                    driver.source,
                    function(source) {
                        var str = source.name + ' (';
        
                        if (driver.id == SCOOPIT_DRIVER_ID) {
                            if (collectedSource.params.url != undefined)
                                str += collectedSource.params.url;
                            else if (collectedSource.params.user != undefined)
                                str += collectedSource.params.user;
                        }

                        str += ')';

                        callback(str);
                    },
                    function(err, details) {
                        displayError('Unable to load source: ' + err);
                    }
                );
            },
            function(err, details) {
                displayError('Unable to load source driver: ' + err);
            }
        );
    }

    function unlinkedDocuments(collection, documents) {
        var docs = Object.keys(documents);
        var index;

        for(let doc in collection.posts) {
            index = docs.indexOf(doc);
            docs.splice(index, 1);
        }

        return docs;
    }

    function collectionTags(collection, callback) {
        var tags = new Set([]);

        for (let id in collection.posts) {
            for(let tag of collection.posts[id].tags) {
                tags.add(tag);
            }
        }

        return tags;
    }

    function textToTag(text, success, error) {
        api.getTag(
            text,
            function(tag) {
                if(tag == undefined) {
                    return success({
                        id: '',
                        text: text,
                        usls: new Set([])
                    });
                }

                success(jsonTagToJS(tag));
            },
            function(err, details) {
                error(err, details);
            }
        );
    }

    function jsonTagToJS(tag) {
        tag.usls = new Set(tag.usls);
        return tag; 
    }

    function removeUSLFromTag(usl, tag, success, error) {
        if(!tag.id) {
            throw 'Cannot remove an USL to the tag ' + tagText;
        }
        if(!tag.usls.delete(usl)) {
            throw 'Cannot remove an USL to the tag ' + tagText;
        }

        // No USLS anymore, delete tag
        if(tag.usls.size == 0) {
            api.deleteTag(tag.id, success, error);
            return;
        }
        
        tag.usls = [...tag.usls];
        api.updateTag(tag, success, error);
    }

    function addUSLToTag(usl, tag, success, error) {
        if(tag.usls.has(usl)) {
            throw 'The USL is already linked to the tag.';
        }

        tag.usls.add(usl);
        var apiCall;

        if(!tag.id) {
            delete tag.id;
            apiCall = api.createTag;
        } else {
            apiCall = api.updateTag;
        }

        tag.usls = [...tag.usls];
        apiCall(tag, success, error);
    }

    // Renderers

    function renderCollectionList(collections) {
        var list = $('#collection-list');
        list.empty();
        
        var li, a, collection;

        for(let id in collections) {
            collection = collections[id];

            li = document.createElement('li');
            a = document.createElement('a');
            a.setAttribute('data-id', collection.id);
            a.setAttribute('href', '');
            a.innerHTML = collection.title;

            (function(collection) {
                $(a).click(function(e) {
                    e.preventDefault();
                    renderCollection(collection);
                });
            })(collection);

            li.appendChild(a);
            list.append(li);
        }
    }

    function togglePostVisibility(post, collection, visible) {
        post.hidden = !visible;

        api.updateCollection(
            collection,
            function(data) {
                renderDocumentList(data);
                if(visible) {
                    renderPost(post.document, data);
                } else {
                    $('#post').hide();
                }
                displayMessage('Document removed from collection successfully!');
            },
            function(err, details) {
                displayError('Unable to update collection: ' + err);
            }
        );
    }

    function buildAddUSLForm() {
        var form = document.createElement('form');

        var input = document.createElement('input');
        input.setAttribute('type', 'text');
        input.setAttribute('name', 'usl');
        form.appendChild(input);

        var err = document.createElement('div');
        err.setAttribute('class', 'field-errors');
        form.appendChild(err);

        input = document.createElement('input');
        input.setAttribute('type', 'submit');
        input.setAttribute('value', 'Add');
        form.appendChild(input);

        return $(form);
    }

    function buildTagUSLList(tag, editorTags) {
        var usls = tag.usls;
        var ul = document.createElement('ul');
        var li, child;

        for(let usl of usls) {
            li = document.createElement('li');

            child = document.createElement('span');
            child.innerHTML = usl;
            li.appendChild(child);

            child = document.createElement('a');
            child.setAttribute('href', '')
            child.setAttribute('class', 'hide')
            child.innerHTML = 'X';
            (function(usl) {
                $(child).click(function(e) {
                    e.preventDefault();

                    try {
                        removeUSLFromTag(
                            usl, tag,
                            function(tag) {
                                displayMessage('USL removed successfully to tag!');
                                renderTagEditor(editorTags);
                            },
                            function(err, details) {
                                displayError('Unable to update tag: ' + err);
                            }
                        );
                    } catch(err) {
                        displayError(err);
                    }
                });
            })(usl);
            li.appendChild(child);

            ul.appendChild(li);
        }

        return ul;
    }

    function renderTagEditor(tags) {
        var div = $('#tag-editor');
        var table = div.find('table');
        table.empty();
        var tr, td, form, tag;

        for(let text of tags) {
            (function(text) {
                textToTag(
                    text,
                    function(tag) {
                        tr = $(document.createElement('tr'));

                        td = document.createElement('td');
                        td.innerHTML = text;
                        tr.append(td);

                        td = $(document.createElement('td'));
                        form = buildAddUSLForm();
                        (function(tag, form) {
                            form.submit(function(e) {
                                e.preventDefault();
                                var data = parseAddUSLForm(form);

                                try {
                                    addUSLToTag(
                                        data.usl, tag,
                                        function(tag) {
                                            displayMessage('USL added successfully to tag!');
                                            cleanForm(form);
                                            renderTagEditor(tags);
                                        },
                                        function(err, details) {
                                            displayError('Unable to update tag: ' + err);
                                        }
                                    );
                                } catch(err) {
                                    displayFormErrors(form, {usl: err});
                                }
                            });
                        })(tag, form);
                        td.append(form);
                        td.append(buildTagUSLList(tag, tags));
                        tr.append(td);

                        table.append(tr);
                    },
                    function(err, details) {
                        displayError('Unable to load tags: ' + err);
                    }
                );
            })(text);
        }
    }

    function renderDocumentList(collection) {
        var li, a, span, post;
        $('#collection-posts').empty();

        for(let docId in collection.posts) {
            post = collection.posts[docId];
            li = document.createElement('li');

            if(!post.hidden) {
                a = document.createElement('a');
                a.setAttribute('data-id', docId);
                a.setAttribute('href', '');

                (function(a) {
                    api.getDocument(docId, function(doc) {
                        a.innerHTML = doc.title ? doc.title : DEFAULT_DOCUMENT_TITLE;
                    }, function(err, details) {
                        displayError('Unable to load document: ' + err);
                    });
                })(a);

                (function(id, collection) {
                    $(a).click(function(e) {
                        e.preventDefault();
                        renderPost(id, collection);
                    });
                })(docId, collection);

                li.appendChild(a);

                a = document.createElement('a');
                a.setAttribute('data-id', docId);
                a.setAttribute('href', '');
                a.setAttribute('class', 'hide');
                a.innerHTML = 'hide';

                (function(post, collection) {
                    $(a).click(function(e) {
                        e.preventDefault();
                        togglePostVisibility(post, collection, false);
                    });
                })(post, collection);

                li.appendChild(a);
            } else {
                span = document.createElement('span');

                (function(el) {
                    api.getDocument(docId, function(doc) {
                        el.innerHTML = doc.title ? doc.title : DEFAULT_DOCUMENT_TITLE + ' ';
                    }, function(err, details) {
                        displayError('Unable to load document: ' + err);
                    });
                })(span);

                li.appendChild(span);
                
                a = document.createElement('a');
                a.setAttribute('data-id', docId);
                a.setAttribute('href', '');
                a.setAttribute('class', 'show');
                a.innerHTML = 'show';

                (function(post, collection) {
                    $(a).click(function(e) {
                        e.preventDefault();
                        togglePostVisibility(post, collection, true);
                    });
                })(post, collection);

                li.appendChild(a);
            }
            
            $('#collection-posts').append(li);
        }
    }
    
    function renderSourceList(collection) {
        var li, a, source;
        $('#collection-sources').empty();

        for(let i in collection.sources) {
            source = collection.sources[i];

            li = document.createElement('li');

            a = document.createElement('a');
            a.setAttribute('href', '');

            (function(a, source) {
                collectedSourceToStr(source, function(str) {
                    a.innerHTML = str;
                });
            })(a, source);

            (function(source) {
                $(a).click(function(e) {
                    e.preventDefault();

                    api.requestSource(
                        collection,
                        api.getSourceDriver(source.driver),
                        source.params,
                        function(resp) {
                            displayMessage('Source being collected... Reload the page to see new documents.');
                        },
                        function(err, details) {
                            displayError('Unable to request source: ' + err);
                        }
                    );
                });
            })(source);

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
                        function(collection) {
                            renderSourceList(collection);
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

    function renderCollectionForm(collection) {
        $('#edit-collection-form input[name="id"]').val(collection.id);
        $('#edit-collection-form input[name="title"]').val(collection.title);
        $('#edit-collection-form input[name="authors"]').val(authorsToStr(collection.authors));
    }

    function renderCollection(collection) {
        if(collection == null) return;

        currentCollection = collection;

        $('#collection-created-on span').html(collection.created_on);
        $('#collection-updated-on span').html(collection.updated_on);

        renderCollectionForm(collection);
        renderSourceList(collection);
        renderDocumentList(collection);
        renderTagEditor(collectionTags(collection)); 
        
        $('#post').hide();
        $('#add-document').hide();
        $('#add-source').hide();
        $('#tag-editor').hide();
        $('#collection').show();
        $('#collection').data('id', collection.id);
    }

    function renderPost(id, collection) {
        var post = collection.posts[id];
        var form = $('#edit-post-form');

        for(let key in post) {
            form.find('*[name="' + key + '"]').val(post[key]);
        }
        form.find('*[name="url_collected"]').val(post.url);

        api.getDocument(
            post.document,
            function(doc) {
                renderDocumentForm(doc);
                $('#post').show();
                $('#post').data('document', post.document);
            },
            function(err, details) {
                displayError('Unable to load document: ' + err);
            }
        );

        renderTagEditor(post.tags);
    }
    
    function renderDocumentForm(doc) {
        var form = $('#edit-document-form');

        for(let key in doc) {
            form.find('*[name="' + key + '"]').val(doc[key]);
        }
        form.find('*[name="authors"]').val(authorsToStr(doc.authors));
        form.find('*[name="keywords"]').val(keywordsToStr(doc.keywords));
    }


    function renderCollectDocumentForm() {
        api.listDocuments(function(documents) {
            var docs = unlinkedDocuments(currentCollection, documents);

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
        }, function(err, details) {
            displayError('Unable to load documents: ' + err);
        });
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

    // Parsers

    function parseAddUSLForm(form) {
        var data = {};

        data.usl = form.find('*[name="usl"]').val().trim();

        return data;
    }

    function parseCollectionForm(form) {
        var data = {};

        data.id = form.find('*[name="id"]').val();
        data.title = form.find('*[name="title"]').val().trim();
        data.authors = authorsToArray(form.find('*[name="authors"]').val());

        return data;
    }
    
    function parseDocumentForm(form) {
        var doc = {};

        doc.id = form.find('*[name="id"]').val();
        doc.title = form.find('*[name="title"]').val().trim();
        doc.authors = authorsToArray(form.find('*[name="authors"]').val());
        doc.created_on = form.find('*[name="created_on"]').val();
        doc.url = form.find('*[name="url"]').val();
        doc.keywords = keywordsToArray(form.find('*[name="keywords"]').val());
        doc.language = form.find('*[name="language"]').val();

        if(!doc.created_on) doc.created_on = null;
        if(!doc.language) doc.language = null;

        return doc;
    }

    function parsePostForm(form) {
        var data = {};
        
        data.document = form.find('*[name="document"]').val();
        data.collected_on = form.find('*[name="collected_on"]').val();
        data.url = form.find('*[name="url_collected"]').val();
        data.tags = tagsToArray(form.find('*[name="tags"]').val());
        data.image = form.find('*[name="image"]').val();
        data.description = form.find('*[name="description"]').val();

        if(!data.collected_on) data.collected_on = new Date().toJSON().split('T')[0];
        if(!data.image) data.image = null;
        if(!data.url) data.url = null;

        return data;
    }

    function parseCollectDocumentForm(form) {
        return {
            doc: parseDocumentForm(form),
            post: parsePostForm(form)
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
    
    // Events

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

        api.updateCollection(
            parseCollectionForm(form),
            function(data) {
                api.listCollections(
                    renderCollectionList,
                    function(err, details) {
                        displayError('Unable to load collections: ' + err);
                    }
                );
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
        var post = parsedForm.post;

        function createDocumentCallback(doc) {
            post.document = doc.id;

            api.createPost(
                post,
                currentCollection,
                function(collection) {
                    currentCollection = collection;
                    renderDocumentList(collection);
                    renderPost(doc.id, collection);
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
            api.getDocument(
                doc.id,
                createDocumentCallback,
                function(err, details) {
                    displayError('Unable to load document: ' + err);
                }
            );
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
    
    $('#edit-post-form').submit(function(e) {
        e.preventDefault();

        var form = $(this);
        var post = parsePostForm(form);

        api.updatePost(post, currentCollection, function(collection) {
            currentCollection = collection;
            cleanForm(form);
            renderPost(post.document, currentCollection);
            displayMessage('Post updated successfully!');
        }, function(err, details) {
            displayError('Unable to update document: ' + err);
            displayFormErrors(form, details);
        });
    });
    
    $('#edit-document-form').submit(function(e) {
        e.preventDefault();

        var form = $(this);
        var data = parseDocumentForm(form);

        api.updateDocument(data, function(doc) {
            cleanFormErrors(form);
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

    $('#tag-editor-button').click(function(e) {
        $('#tag-editor').toggle();
    });

    $('#collect-document-button').click(function(e) {
        renderCollectDocumentForm();
        $('#collect-document').toggle();
    });

    function addSourceFactory(form, driver, parser) {
        form.submit(function(e) {
            e.preventDefault();

            var source = {
                driver: driver,
                params: parser(form) 
            };
            currentCollection.sources.push(source);

            api.updateCollection(currentCollection, function(collection) {
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

    api.listCollections(function(collections) {
        renderCollectionList(collections);

        $('#messages').html('');
        $('#sidebar').css('display', 'inline-block');
        $('#main').css('display', 'inline-block');
    }, function(err) {
        displayError('Unable to load collections: ' + err); 
    });
});
