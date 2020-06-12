var ObserverCopy;
// 0: unsorted    1: Descending order   -1: Ascending order
var amount_sort = 0;     
var registration_sort = 0;

function Init(Observer){
    var init = {};
    ObserverCopy = Observer;

    var mode = getParams("mode");
    var value = getParams("value");

    $("#search_input").val(value);
    $('#mode-select').val(mode);

    if(mode == "Boolean"){
        Observer.fireEvent("Boolean", value, Init);
    }
    else if(mode == "Tolerant"){
        Observer.fireEvent("Tolerant", value, Init);
    }
    else{
        Observer.fireEvent("Query", value, Init);
    }

    init.onMessage = function(message, data, from){
        if(message == "haha"){
            if(from == Boolean_search){
                console.log(data);
            }
        }
    }

    Observer.addView(init);
    return init;
}

function getParams(key) {
    var reg = new RegExp("(^|&)" + key + "=([^&]*)(&|$)");
    var r = encodeURI(window.location.search).substr(1).match(reg);  
    if (r != null) {
        return decodeURI(unescape(r[2]));  
    }
    return null;
}

function search_value(mode, value){
    if(mode == "Boolean"){
        ObserverCopy.fireEvent("Boolean", value, Init);
    }
    else if(mode == "Tolerant"){
        ObserverCopy.fireEvent("Tolerant", value, Init);
    }
    else{
        ObserverCopy.fireEvent("Query", value, Init);
    }
}

function getTableData(){
    var result = new Array();
    $("#result-table").find("tr").each(function(){
        var tmp = new Array();
        $(this).find("td").each(function(){
            tmp.push($(this).text());
        })
        // 不是th的值
        if(tmp.length != 0){
            result.push({
                "amount": tmp[0],
                "date": tmp[1].replace(/-/g, "/"),   // 2020/05/24形式
                "content": tmp[2]
            })
        }
    })
    return result;
}

// 排序的比较函数 1: 降序  -1: 升序
function compare(property, order){
    if(property == "amount"){
        if(order == 1){
            return function(obj1, obj2){
                var val1 = Number(obj1[property]);
                var val2 = Number(obj2[property]);
                return val2 - val1;
            }
        }
        else if(order == -1){
            return function(obj1, obj2){
                var val1 = Number(obj1[property]);
                var val2 = Number(obj2[property]);
                return val1 - val2;
            }
        }
    }
    else if(property == "date"){
        if(order == 1){
            return function(obj1, obj2){
                var val1 = new Date(obj1[property]);
                var val2 = new Date(obj2[property]);
                return val2 - val1;
            }
        }
        else if(order == -1){
            return function(obj1, obj2){
                var val1 = new Date(obj1[property]);
                var val2 = new Date(obj2[property]);
                return val1 - val2;
            }
        }
    }
}

function updateTable(table){
    $("#result-table  tr:not(:first)").remove();      // 删去除表头之外的数据
    // 新建单元格
    for(var i = 1; i <= table.length; i++){
        var insertTr = document.getElementById("result-table").insertRow(i);
        for(var j = 0; j < 3; j++){
            insertTr.insertCell(j);
        }
    }
    // 写入新数据
    for(var i = 0; i < table.length + 1; i++){
        $("#result-table tr:eq(" + (i + 1) + ") td:nth-child(1)").html(table[i]["amount"]);
        $("#result-table tr:eq(" + (i + 1) + ") td:nth-child(2)").html(table[i]["date"]);
        $("#result-table tr:eq(" + (i + 1) + ") td:nth-child(3)").html(table[i]["content"]);
    }
}

function rank_amount(){
    var table_data = getTableData();
    // 设置默认降序
    if(amount_sort == 0){
        amount_sort = 1;
        $("th#amount svg use").attr("xlink:href", "#iconpaixu-xia");
        table_data.sort(compare("amount", 1));
    }
    else if(amount_sort == 1){
        amount_sort = -1;
        $("th#amount svg use").attr("xlink:href", "#iconpaixu-shang");
        table_data.sort(compare("amount", -1));
    }
    else{
        amount_sort = 1;
        $("th#amount svg use").attr("xlink:href", "#iconpaixu-xia");
        table_data.sort(compare("amount", 1));
    }

    // 网页更新排序的数据
    updateTable(table_data);
}

function rank_registration(){
    var table_data = getTableData();
    // 设置默认降序
    if(registration_sort == 0){
        registration_sort = 1;
        $("th#registration svg use").attr("xlink:href", "#iconpaixu-xia");
        table_data.sort(compare("date", 1));
    }
    else if(registration_sort == 1){
        registration_sort = -1;
        $("th#registration svg use").attr("xlink:href", "#iconpaixu-shang");
        table_data.sort(compare("date", -1));
    }
    else{
        registration_sort = 1;
        $("th#registration svg use").attr("xlink:href", "#iconpaixu-xia");
        table_data.sort(compare("date", 1));
    }

    // 网页更新排序的数据
    updateTable(table_data);
}
