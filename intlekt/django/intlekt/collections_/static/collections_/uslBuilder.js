var USLBuilder = function(initialData, CONCAT_CHAR) {
    var module = {};

    var hintDiv = document.createElement('div');
    var table = document.createElement('table');
    var tagRow = document.createElement('tr');
    var uslRow = document.createElement('tr');
    table.appendChild(tagRow);
    table.appendChild(uslRow);

    var data = {};
    
    for(let text in initialData) {
        data[text] = {
            usls: initialData[text],
            choice: 0
        };
    }

    function buildUSLList(obj) {
        var ul = document.createElement('ul');
        var li;

        for(let i in obj.usls) {
            li = document.createElement('li');
            li.innerHTML = obj.usls[i];
            if(i == obj.choice) li.setAttribute('class', 'selected_usl'); 

            (function(i) {
                $(li).click(function(e) {
                    e.preventDefault();
                    obj.choice = i;
                    module.render();
                });
            })(i);

            ul.appendChild(li);
        }

        return ul;
    }

    function getHint() {
        var selectedUSLs = [];
        var obj;

        for(let text in data) {
            obj = data[text];
            if(obj.usls[obj.choice])
                selectedUSLs.push(obj.usls[obj.choice]);
        }

        return selectedUSLs.join(CONCAT_CHAR); 
    }

    module.render = function() {
        hintDiv.innerHTML = getHint();

        $(tagRow).find('td').remove();
        $(uslRow).find('td').remove();
        var td;

        for(let text in data) {
            td = document.createElement('td');
            if(data[text].usls.length == 0) td.setAttribute('class', 'no_usl');
            td.innerHTML = text;
            tagRow.appendChild(td);

            td = document.createElement('td');
            td.appendChild(buildUSLList(data[text]));
            uslRow.appendChild(td);
        }

        return {hintDiv: hintDiv, table: table};
    }

    return module;
};
