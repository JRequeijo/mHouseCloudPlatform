//// DEPRECATED ONES
function sendDelete(ele_id, path){
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 204) {
            return true;
        }
    };
    req.open("DELETE", path+ele_id+"/", true);
    var csrftoken = getCookie('csrftoken');
    //req.setRequestHeader("Content-type", "application/json");
    req.setRequestHeader("X-CSRFToken", csrftoken);
    req.send();
}

function deleteElemAndRedirect(ele_id, host, red_uri, secure){

    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 204) {
            if(secure){
                var url = "https://"+host+red_uri
            }else{
                var url = "http://"+host+red_uri
            }
            window.location.replace(url);
        }
    };
    req.open("DELETE", red_uri+ele_id+"/", true);
    var csrftoken = getCookie('csrftoken');
    //req.setRequestHeader("Content-type", "application/json");
    req.setRequestHeader("X-CSRFToken", csrftoken);
    req.send();
}

function checkOptSelected(){
    var table = document.getElementById('elementsTable');
    var delBut = document.getElementById('delButton');

    var selected = false;
    var rowList = table.getElementsByTagName('tr');
    for(i=1; i < rowList.length; i++){
        var cells = rowList[i].getElementsByTagName('td');
        if(cells[0].firstChild.checked){
            selected = true;
            break;
        }
    }
    if(selected){
        delBut.removeAttribute("disabled");
    }else{
        delBut.setAttribute("disabled", "");
    }
}

function selectAll(check){
    var table = document.getElementById('elementsTable');
    var delBut = document.getElementById('delButton');
    var rowList = table.getElementsByTagName('tr');
    for(i=1; i < rowList.length; i++){
        var cells = rowList[i].getElementsByTagName('td');
        cells[0].firstChild.checked = check;
    }
    if(check){
        delBut.removeAttribute("disabled");
    }else{
        delBut.setAttribute("disabled", "");
    }
}

function deleteElements(uri){
    var table = document.getElementById('elementsTable');

    var rowList = table.getElementsByTagName('tr');
    for(i=1; i < rowList.length; i++){
        var cells = rowList[i].getElementsByTagName('td');
        if(cells[0].firstChild.checked){
            var ele_id = cells[1].innerText;
            sendDelete(ele_id, uri);
        }
    }

    closeModal('deleteModal');

    window.location.reload()
}

function updateElemAndRedirect(ele_id, host, red_uri, user, secure){

    var form = document.getElementById('actForm');

    var inpts = form.getElementsByTagName('input');
    var sels =form.getElementsByTagName('select');
    var elems = [];
    elems.push.apply(elems, inpts);
    elems.push.apply(elems, sels);
    var data = {}
    data['user']=user;
    for(i=0; i<elems.length; i++){
        data[elems[i].name] = elems[i].value;
    }

    content = JSON.stringify(data);
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4) {
            if(this.status == 200){
                if(secure){
                    var url = "https://"+host+red_uri
                }else{
                    var url = "http://"+host+red_uri
                }
                window.location.replace(url);
            }
            if(this.status == 400){
                var htexts = document.getElementsByClassName('help-block');
                for(i=htexts.length-1; i>=0; i--){
                    var par = htexts[i].parentElement
                    par.setAttribute('class', 'col-md-6');
                    par.removeChild(htexts[i]);
                }
                var resp = JSON.parse(req.responseText);
                for(var key in resp){
                    var span = document.createElement('span');
                    span.setAttribute('class', 'help-block');
                    var msg = document.createElement('strong');
                    msg.innerHTML = resp[key];
                    span.appendChild(msg);

                    var inpt = document.getElementById('id_'+key);
                    inpt.parentElement.setAttribute('class', 'col-md-6 has-error')
                    inpt.parentElement.appendChild(span);
                }
                closeModal('updateModal');
            }
        }
    };
    req.open("PUT", red_uri+ele_id+"/", true);
    
    var csrftoken = getCookie('csrftoken');
    
    req.setRequestHeader("Content-type", "application/json");
    req.setRequestHeader("accept", "application/json");

    req.setRequestHeader("X-CSRFToken", csrftoken);
    req.send(content);
}



/// CURRENT ONES
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function closeModal(modal_id){
    var modal = document.getElementById(modal_id);
    modal.className = 'modal fade';
    modal.style.display = 'none';
    var body = document.getElementsByTagName('body')[0];
    body.className = '';
    body.removeChild(document.getElementsByClassName('modal-backdrop fade in')[0]);
}

function goToURL(host, red_uri, secure){
    if(secure){
        var url = "https://"+host+red_uri
    }else{
        var url = "http://"+host+red_uri
    }
    window.location.replace(url);
}

//AJAX FUNCTIONS
function newElement(elementName, host, redirect_uri, secure){
    var modal = document.getElementById(elementName+"CreationModal");

    var json_data = get_input_data(modal);

    clean_error_divs(modal);

    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4){
            if(this.status == 200) {
                if(secure){
                    var url = "https://"+host+redirect_uri
                }else{
                    var url = "http://"+host+redirect_uri
                }
                window.location.replace(url);
            }else{
                var resp = JSON.parse(this.responseText)
                var err_div = null;
                for(var ele in resp){
                    err_div = document.getElementById(elementName+"-"+String(ele)+"-err")
                    err_div.parentElement.setAttribute("class", "has-error")
                    err_div.firstElementChild.innerHTML = resp[ele]
                }
            }
        }
    };
    req.open("POST", get_API_uri(elementName), true);
    var csrftoken = getCookie('csrftoken');
    req.setRequestHeader("Content-type", "application/json");
    req.setRequestHeader("X-CSRFToken", csrftoken);
    req.send(json_data);
}

function updateElement(elementName, elementId, callback, host, redirect_uri, secure, partial){
    var form = document.getElementById(elementName+"UpdateForm");

    var json_data = get_input_data(form);

    clean_error_divs(form);

    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4){
            if(this.status == 200) {
                return callback(host, redirect_uri, secure);
            }else{
                var resp = JSON.parse(this.responseText);
                try{
                    var err_div = null;
                    for(var ele in resp){
                        err_div = document.getElementById(elementName+"-"+String(ele)+"-err");
                        err_div.parentElement.setAttribute("class", "has-error");
                        err_div.firstElementChild.innerHTML = resp[ele];
                    }
                    closeModal("updateModal");
                }catch(err){
                    closeModal("updateModal");
                    if(resp["detail"] != null){
                        window.alert(resp["detail"]);
                    }else if(resp["error_msg"] != null){
                        window.alert(resp["error_msg"]);
                    }else{
                        window.alert(this.responseText);
                    }
                }
            }
        }
    };
    if(partial){
        req.open("PATCH", get_API_uri(elementName)+String(elementId)+"/", true);
    }else{
        req.open("PUT", get_API_uri(elementName)+String(elementId)+"/", true);
    }
    var csrftoken = getCookie('csrftoken');
    req.setRequestHeader("Content-type", "application/json");
    req.setRequestHeader("X-CSRFToken", csrftoken);
    req.send(json_data);
}

function deleteElement(elementName, elementId, callback, host, redirect_uri, secure){
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4){
            if(this.status == 204) {
                if(callback){
                    return callback(host, redirect_uri, secure);
                }else{
                    return true;
                }
            }else{
                console.error("ERROR ("+String(this.status)+"):"+this.responseText);
                return false;
            }
        }
    };
    req.open("DELETE", get_API_uri(elementName)+String(elementId)+"/", true);
    var csrftoken = getCookie('csrftoken');
    req.setRequestHeader("Content-type", "application/json");
    req.setRequestHeader("X-CSRFToken", csrftoken);
    req.send();
}

function checkElementState(elementId, type, callback){
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4){
            if(this.status == 200){
                if(callback){
                    return callback(this, elementId);
                }else{
                    return true;
                }
            }else{
                console.error("ERROR ("+String(this.status)+"):"+this.responseText);
                return false;
            }
        }
    };
    req.open("GET", get_API_uri(type)+String(elementId)+"/state/", true);
    req.setRequestHeader("Accept", "application/json");
    req.send();
}

function updateDeviceProperty(propertyName, deviceId){
    
    var prop_value = document.getElementById("property-"+propertyName).value;
    
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4){
            if (this.status == 200) {
                window.alert("Property Updated");
                return true;
            }else{
                var resp = JSON.parse(this.responseText);
                window.alert(resp["error_msg"]);
                return false;
            }
        }
    };
    var dict = {};
    dict[propertyName] = prop_value;
    var data = JSON.stringify(dict);

    // window.alert(data);
    req.open("PATCH", get_API_uri("device")+deviceId+"/state/", true);
    var csrftoken = getCookie("csrftoken");
    req.setRequestHeader("Content-type", "application/json");
    req.setRequestHeader("X-CSRFToken", csrftoken);
    req.setRequestHeader("accept", "application/json");
    req.send(data);
}

// OTHERS
function checkOptionsSelected(){
    var selected = false;
    var inpts = document.getElementsByClassName("checkInpt");
    var delBtn = document.getElementById("deleteBtn");
    for(var i=0; i<inpts.length; i++){
        if(inpts[i].checked){
            selected = true;
            break;
        }
    }

    if(selected){
        delBtn.removeAttribute("disabled");
    }else{
        delBtn.setAttribute("disabled", "");
    }
}

function markForDeletion(checkBtn){
    var tr = checkBtn.parentElement.parentElement;
    
    if(checkBtn.checked){
        tr.setAttribute("class", "deletion-marked");
    }else{
        tr.removeAttribute("class");
    }

    checkOptionsSelected();
}

function markAllForDeletion(check){
    var inpts = document.getElementsByClassName("checkInpt");
    var checkBtns = [];
    for(var i=0; i<inpts.length; i++){
        checkBtns.push(inpts[i]);
    }

    for(var i=0; i<checkBtns.length; i++){
        checkBtns[i].checked = check;
        markForDeletion(checkBtns[i]);
    }
}

function deleteMarkedElements(elementName){
    var elems = document.getElementsByClassName("deletion-marked");
    var id = null;
    while(elems.length>0){
        id = elems[0].children[1].innerHTML;
        deleteElement(elementName, id);
        elems[0].parentElement.removeChild(elems[0]);
    }
    closeModal("deleteModal");

    var masterCheck = document.getElementById("masterCheckInpt");
    masterCheck.checked = false;
    
    checkOptionsSelected();
}


function getSelectValues(select) {
    var result = [];
    var options = select && select.options;
    var opt;

    for (var i=0, iLen=options.length; i<iLen; i++) {
        opt = options[i];

        if (opt.selected) {
            if(opt.value == ""){
                result = [];
                break;
            }else{
                result.push(parseInt(opt.value));
            }
        }
    }
    return result;
}

function clean_error_divs(modal){
    var err_divs = modal.getElementsByClassName("err-div");
    var err_div = null;
    for(var i = 0; i<err_divs.length; i++){
        err_div = err_divs[i];
        err_div.parentElement.setAttribute("class", "")
        err_div.firstElementChild.innerHTML = ""
    }

    return;
}

function get_input_data(modal){
    var inpts = modal.getElementsByTagName("input");
    var sels = modal.getElementsByTagName("select");
    
    var elems = [];
    elems.push.apply(elems, inpts);
    elems.push.apply(elems, sels);
    
    var data = {}
    var ele = null;
    for(i=0; i<elems.length; i++){
        ele = elems[i];
        if(ele.tagName == "SELECT"){
            if(ele.hasAttribute("multiple")){
                data[ele.name] = getSelectValues(ele);
            }else{
                var try_id = parseInt(ele.value);
                if(isNaN(try_id)){
                    data[ele.name] = ele.value;
                }else{
                    data[ele.name] = try_id;
                }
            }
        }else{
            if(ele.type == "text"){
                data[ele.name] = ele.value;
            }
            if(ele.type == "number"){
                data[ele.name] = Number(ele.value);
            }
        }
    }

    return JSON.stringify(data);
}

function get_API_uri(elementName){
    var base_uri = "/api";
    
    // SPACE ELEMENTS
    if(elementName == "house"){
        return base_uri+"/houses/";
    }
    if(elementName == "area"){
        return base_uri+"/areas/";
    }
    if(elementName == "division"){
        return base_uri+"/divisions/";
    }

    //SERVERS AND DEVICES
    if(elementName == "server"){
        return base_uri+"/servers/";
    }
    if(elementName == "device"){
        return base_uri+"/devices/";
    }

    //SERVICES
    if(elementName == "service"){
        return base_uri+"/services/";
    }
    
    // CONFIGS
    base_uri = base_uri+"/configs";
    if(elementName == "devicetype"){
        return base_uri+"/device_types/";
    }
    if(elementName == "proptype"){
        return base_uri+"/property_types/";
    }
    if(elementName == "scalar"){
        return base_uri+"/scalars/";
    }
    if(elementName == "enum"){
        return base_uri+"/enums/";
    }
    if(elementName == "choice"){
        return base_uri+"/choices/";
    }
}

function redirect(host, redirect_uri, secure){
    if(secure){
        var url = "https://"+host+redirect_uri
    }else{
        var url = "http://"+host+redirect_uri
    }
    window.location.replace(url);
}

function checkAllElementsState(type){
    var trows = document.getElementsByClassName("elementRow");
    for(var i=0; i<trows.length; i++){
        checkElementState(trows[i].firstElementChild.innerHTML, type, updateGlyphicons);
    }
}

function updateGlyphicons(response, elementId){
    var state_col = document.getElementById("stateCol-"+elementId);
    resp = JSON.parse(response.responseText);
    if(resp["status"] == "running"){
        if(state_col.firstChild.className != 'glyphicon glyphicon-ok'){
            var span = state_col.firstElementChild
            span.setAttribute("class", "glyphicon glyphicon-ok");
            span.setAttribute("style", "color: green;");

            state_col.lastElementChild.innerHTML = ' Running';
        }
    }else{
        if(state_col.firstChild.className != 'glyphicon glyphicon-remove'){
            var span = state_col.firstElementChild
            span.setAttribute("class", "glyphicon glyphicon-remove");
            span.setAttribute("style", "color: red;");

            state_col.lastElementChild.innerHTML = ' Down';
        }
    }
}

function updateGlyphiconsAndButtons(response, serverId){
    var state_col = document.getElementById("stateCol-"+serverId);
    var updt_btns = document.getElementsByClassName("update-btn");
    var del_btns = document.getElementsByClassName("delete-btn");

    resp = JSON.parse(response.responseText);
    if(resp["status"] == "running"){
        if(state_col.firstChild.className != 'glyphicon glyphicon-ok'){
            var span = state_col.firstElementChild
            span.setAttribute("class", "glyphicon glyphicon-ok");
            span.setAttribute("style", "color: green;");

            state_col.lastElementChild.innerHTML = ' Running';
        }
        for(var i=0; i<updt_btns.length; i++){
            updt_btns[i].removeAttribute("disabled");
        }
        for(var i=0; i<del_btns.length; i++){
            del_btns[i].setAttribute("disabled", "");
        }
    }else{
        if(state_col.firstChild.className != 'glyphicon glyphicon-remove'){
            var span = state_col.firstElementChild
            span.setAttribute("class", "glyphicon glyphicon-remove");
            span.setAttribute("style", "color: red;");

            state_col.lastElementChild.innerHTML = ' Down';
        }
        for(var i=0; i<updt_btns.length; i++){
            updt_btns[i].setAttribute("disabled", "");
        }
        for(var i=0; i<del_btns.length; i++){
            del_btns[i].removeAttribute("disabled");
        }
    }
}

function updateAllDeviceDetailView(response, deviceId){
    var state_col = document.getElementById("stateCol-"+deviceId);
    var updt_btns = document.getElementsByClassName("update-btn");
    var radio_btns = document.getElementsByClassName("radio-setter");
    var del_btns = document.getElementsByClassName("delete-btn");

    resp = JSON.parse(response.responseText);
    if(resp["status"] == "running"){
        if(state_col.firstChild.className != 'glyphicon glyphicon-ok'){
            var span = state_col.firstElementChild
            span.setAttribute("class", "glyphicon glyphicon-ok");
            span.setAttribute("style", "color: green;");

            state_col.lastElementChild.innerHTML = ' Running';
        }
        for(var i=0; i<updt_btns.length; i++){
            updt_btns[i].removeAttribute("disabled");
        }
        for(var i=0; i<del_btns.length; i++){
            del_btns[i].setAttribute("disabled", "");
        }
        var prop_div = null;
        for(var prop in resp["state"]){
            prop_div = document.getElementById("property-"+String(prop)+"-div");
            prop_div.firstElementChild.innerHTML = resp["state"][prop];
            if(prop_div.className == "enum"){
                var divs = prop_div.lastElementChild.children;
                for(var i = 0; i<divs.length; i++){
                    var inpt = divs[i].firstElementChild.firstElementChild;
                    if(inpt.value == String(resp["state"][prop])){
                        inpt.checked = true;
                    }
                }
            }
        }
        //blockPropertySetterInpts(false);
    }else{
        if(state_col.firstChild.className != 'glyphicon glyphicon-remove'){
            var span = state_col.firstElementChild
            span.setAttribute("class", "glyphicon glyphicon-remove");
            span.setAttribute("style", "color: red;");

            state_col.lastElementChild.innerHTML = ' Down';
        }
        for(var i=0; i<radio_btns.length; i++){
            radio_btns[i].setAttribute("disabled", "");
        }
        for(var i=0; i<updt_btns.length; i++){
            updt_btns[i].setAttribute("disabled", "");
        }
        for(var i=0; i<del_btns.length; i++){
            del_btns[i].removeAttribute("disabled");
        }
    }
}