function fetchResults(deviceId, with_data){

    if(with_data){
        var start_day = document.getElementById("start_day").value;
        var start_month = document.getElementById("start_month").value;
        var start_year = document.getElementById("start_year").value;
        var end_day = document.getElementById("end_day").value;
        var end_month = document.getElementById("end_month").value;
        var end_year = document.getElementById("end_year").value;
    
        var start = String(start_year)+"-"+String(start_month)+"-"+String(start_day)
        var end = String(end_year)+"-"+String(end_month)+"-"+String(end_day)
    
    }
    
    var n_results = document.getElementById("n_results_to_fetch").value;

    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4){
            if (this.status == 200) {
                var resp = JSON.parse(this.responseText);
                var tableData = document.getElementById("history-table");
                while(tableData.firstChild){
                    tableData.removeChild(tableData.firstChild);
                }
                if(resp[0]){
                    var thead = document.createElement("thead");
                    
                    var th = document.createElement("th");
                    th.innerHTML = "#";
                    thead.appendChild(th);

                    for(var tit in resp[0]["new_state"]){
                        var th = document.createElement("th");
                        th.innerHTML = tit;
                        thead.appendChild(th);
                    }

                    var th = document.createElement("th");
                    th.innerHTML = "Source";
                    thead.appendChild(th);

                    var th = document.createElement("th");
                    th.innerHTML = "Timestamp";
                    thead.appendChild(th);
                    
                    tableData.appendChild(thead);
                    
                    var tbody = document.createElement("tbody");

                    var i = 0;
                    for(var ele in resp){
                        i++;
                        var tr = document.createElement("tr");

                        var td = document.createElement("td");
                        td.innerHTML = i;
                        tr.appendChild(td);

                        for(var val in resp[ele]["new_state"]){
                            var td = document.createElement("td");
                            td.innerHTML = resp[ele]["new_state"][val];
                            tr.appendChild(td);
                        }

                        var td = document.createElement("td");
                        td.innerHTML = resp[ele]["source"];
                        tr.appendChild(td);

                        var td = document.createElement("td");
                        var d = new Date(resp[ele]["timestamp"]);
                        td.innerHTML = String("0" + d.getDay()).slice(-2)+"-"+String("0" + d.getMonth()).slice(-2)+"-"+String("0" + d.getFullYear()).slice(-2)+"&emsp;&emsp;"+String("0" + d.getHours()).slice(-2)+":"+String("0" + d.getMinutes()).slice(-2)+":"+String("0" + d.getSeconds()).slice(-2)+" h";
                        tr.appendChild(td);
                        
                        tbody.appendChild(tr);
                    }

                    tableData.appendChild(tbody);
                }else{
                    tableData.innerHTML = "<b> No Results Found between the provided data interval! </b>";
                }
                return true;
            }else{
                var resp = JSON.parse(this.responseText);
                window.alert(resp["error_msg"]);
                return false;
            }
        }
    };

    var uri = get_API_uri("device")+deviceId+"/history/?";
    if(with_data){
        uri = uri + "start="+start+"&"+"end="+end+"&limit="+n_results;
    }else{
        uri = uri + "limit="+n_results;
    }
    // window.alert(data);
    req.open("GET", uri, true);
    req.setRequestHeader("Content-type", "application/json");
    req.setRequestHeader("accept", "application/json");
    req.send();
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