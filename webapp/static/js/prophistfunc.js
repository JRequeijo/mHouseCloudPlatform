function fetchResultsByNumber(nb_results, deviceId){

    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4){
            if (this.status == 200) {
                var resp = JSON.parse(this.responseText);
                var tableData = document.getElementById("history-table");
                while(tableData.firstChild){
                    tableData.removeChild(tableData.firstChild);
                }
                var i = 0;
                for(var ele in resp){
                    i++;
                    var tr = document.createElement("tr");

                    var td = document.createElement("td");
                    td.innerHTML = i;
                    tr.appendChild(td);

                    var td = document.createElement("td");
                    td.innerHTML = resp[ele]["property_id"];
                    tr.appendChild(td);

                    var td = document.createElement("td");
                    td.innerHTML = resp[ele]["property_name"];
                    tr.appendChild(td);

                    var td = document.createElement("td");
                    td.innerHTML = resp[ele]["new_value"];
                    tr.appendChild(td);

                    var td = document.createElement("td");
                    td.innerHTML = resp[ele]["issuing_mode"];
                    tr.appendChild(td);

                    var td = document.createElement("td");
                    td.innerHTML = resp[ele]["timestamp"];
                    tr.appendChild(td);
                    
                    tableData.appendChild(tr);
                }
                return true;
            }else{
                var resp = JSON.parse(this.responseText);
                window.alert(resp["error_msg"]);
                return false;
            }
        }
    };

    // window.alert(data);
    req.open("GET", get_API_uri("device")+deviceId+"/history/?limit="+nb_results, true);
    var csrftoken = getCookie("csrftoken");
    req.setRequestHeader("Content-type", "application/json");
    req.setRequestHeader("X-CSRFToken", csrftoken);
    req.setRequestHeader("accept", "application/json");
    req.send();
}

function fetchResultsByDate(deviceId){

    var start_day = document.getElementById("start_day").value;
    var start_month = document.getElementById("start_month").value;
    var start_year = document.getElementById("start_year").value;
    var end_day = document.getElementById("end_day").value;
    var end_month = document.getElementById("end_month").value;
    var end_year = document.getElementById("end_year").value;

    var start = String(start_year)+"-"+String(start_month)+"-"+String(start_day)
    var end = String(end_year)+"-"+String(end_month)+"-"+String(end_day)

    console.info(start);
    console.info(end);
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4){
            if (this.status == 200) {
                var resp = JSON.parse(this.responseText);
                var tableData = document.getElementById("history-table");
                while(tableData.firstChild){
                    tableData.removeChild(tableData.firstChild);
                }
                var i = 0;
                for(var ele in resp){
                    i++;
                    var tr = document.createElement("tr");

                    var td = document.createElement("td");
                    td.innerHTML = i;
                    tr.appendChild(td);

                    var td = document.createElement("td");
                    td.innerHTML = resp[ele]["property_id"];
                    tr.appendChild(td);

                    var td = document.createElement("td");
                    td.innerHTML = resp[ele]["property_name"];
                    tr.appendChild(td);

                    var td = document.createElement("td");
                    td.innerHTML = resp[ele]["new_value"];
                    tr.appendChild(td);

                    var td = document.createElement("td");
                    td.innerHTML = resp[ele]["issuing_mode"];
                    tr.appendChild(td);

                    var td = document.createElement("td");
                    td.innerHTML = resp[ele]["timestamp"];
                    tr.appendChild(td);
                    
                    tableData.appendChild(tr);
                }
                return true;
            }else{
                var resp = JSON.parse(this.responseText);
                window.alert(resp["error_msg"]);
                return false;
            }
        }
    };

    // window.alert(data);
    req.open("GET", get_API_uri("device")+deviceId+"/history/?start="+start+"&"+"end="+end, true);
    var csrftoken = getCookie("csrftoken");
    req.setRequestHeader("Content-type", "application/json");
    req.setRequestHeader("X-CSRFToken", csrftoken);
    req.setRequestHeader("accept", "application/json");
    req.send();
}


function sortHistoryTable(sortColumn){
    var tableData = document.getElementById("history-table");
    var rowData = tableData.getElementsByTagName("tr");
    for(var i = 0; i < rowData.length - 1; i++){
        for(var j = 0; j < rowData.length - (i + 1); j++){
            if(Number(rowData.item(j).getElementsByTagName('td').item(sortColumn).innerHTML.replace(/[^0-9\.]+/g, "")) 
                < Number(rowData.item(j+1).getElementsByTagName('td').item(sortColumn).innerHTML.replace(/[^0-9\.]+/g, ""))){
                tableData.insertBefore(rowData.item(j+1),rowData.item(j));
            }
            else if(rowData.item(j).getElementsByTagName('td').item(sortColumn).innerHTML
                < rowData.item(j+1).getElementsByTagName('td').item(sortColumn).innerHTML){
                tableData.insertBefore(rowData.item(j+1),rowData.item(j));
            }
        }
    }
}

function createSelect(){
    var day_sel = document.getElementsByClassName("day_select");
    var month_sel = document.getElementsByClassName("month_select");
    var year_sel = document.getElementsByClassName("year_select");
    for(var j=0; j<day_sel.length; j++){
        for(var i=1; i<=31; i++){
            var opt = document.createElement("option");
            opt.value = i;
            opt.innerHTML = i;
            day_sel[j].appendChild(opt);
        }
    }
    for(var j=0; j<month_sel.length; j++){
        for(var i=1; i<=12; i++){
            var opt = document.createElement("option");
            opt.value = i;
            opt.innerHTML = i;
            month_sel[j].appendChild(opt);
        }
    }
    var now = new Date().getFullYear();
    console.info(now)
    for(var j=0; j<year_sel.length; j++){
        for(var i=2015; i<=now; i++){
            var opt = document.createElement("option");
            opt.value = i;
            opt.innerHTML = i;
            year_sel[j].appendChild(opt);
        }
    } 
}