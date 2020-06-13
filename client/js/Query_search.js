// 0: unsorted    1: Descending order   -1: Ascending order
var query_date_sort = 0;
var query_keys = ["ID", "caseCode", "Title", "Type", "Cause", "Department", "Level", "date", "Content"];

function Query_search(Observer){
    var query_search = {};

    query_search.onMessage = function(message, data, from){
        if(message == "Query"){
            if(from == Init){
                $("#data1-list").hide();
                $("#data2-list").hide();
                $("#query-list").show();

                let obj = {};
                obj.value = JSON.stringify(data);
                $.ajax({
                    type: 'GET',
                    url: 'Query_search',
                    data: obj,
                    dataType: 'json',
                    success: function(evt_data) {
                        var data = evt_data.result;
                        // 创建表格
                        create_query_table();
                        // 插入前20个数据
                        insert_data(data, 0, data.length - 1);

                        $("#result_wait").hide();
                    },
                    error: function(jqXHR) {
                        console.log('post error!!', jqXHR);
                    },
                });
            }
        }
    }

    Observer.addView(query_search);
    return query_search;
}


function create_query_table(){
    $("#query-table tr").remove();    // 清除表格内容
    var table = $("#query-table");
    table.html("<tr>\
                    <th width='10%'>ID</th>\
                    <th width='15%'>案号</th>\
                    <th width='10%'>标题</th>\
                    <th width='6%'>文书类别</th>\
                    <th width='10%'>案由</th>\
                    <th width='10%'>承办部门</th>\
                    <th width='5%'>级别</th>\
                    <th width='10%' id='registration' onclick='rank_date()'>结案日期&nbsp;<svg class='icon sort-icon' aria-hidden='true'><use xlink:href='#iconpaixu'></use></svg></th>\
                    <th width='24%'>Content</th>\
                </tr>");
}

function insert_data(table_data, start, end){
    $("#query-table  tr:not(:first)").remove();      // 删去除表头之外的数据
    // 新建单元格
    for(var i = 1; i <= (end - start + 1); i++){
        var insertTr = document.getElementById("query-table").insertRow(i);

        for(var j = 0; j < 9; j++){
            var insertTd = insertTr.insertCell(j);
            insertTd.onclick = function() { alert($(this).text()) };
        }
    }
    // 写入新数据
    for(var i = 0; i <= (end - start); i++){
        for(var j = 0; j < 9; j++){
            $("#query-table tr:eq(" + (i + 1) + ") td:nth-child(" + (j + 1) + ")").html(table_data[start + i][j + 1]);
        }
    }
}

function getTableData(){
    var result = new Array();
    $("#query-table").find("tr").each(function(){
        var tmp = new Array();
        $(this).find("td").each(function(){
            tmp.push($(this).text());
        })
        // 不是th的值
        if(tmp.length != 0){
            result.push({
                "ID": tmp[0],
                "caseCode": tmp[1],
                "Title": tmp[2],
                "Type": tmp[3],
                "Cause": tmp[4],
                "Department": tmp[5],
                "Level": tmp[6],
                "date": tmp[7],
                "Content": tmp[8]
            })
        }
    })
    return result;
}

function updateTable(table){
    $("#query-table  tr:not(:first)").remove();      // 删去除表头之外的数据
    // 新建单元格
    for(var i = 1; i <= table.length; i++){
        var insertTr = document.getElementById("query-table").insertRow(i);
        for(var j = 0; j < 9; j++){
            var insertTd = insertTr.insertCell(j);
            insertTd.onclick = function() { alert($(this).text()) };
        }
    }
    // 写入新数据
    for(var i = 0; i < table.length; i++){
        for(var j = 0; j < 9; j++){
            $("#query-table tr:eq(" + (i + 1) + ") td:nth-child(" + (j + 1) + ")").html(table[i][query_keys[j]]);
        }
    }

    $("#result_wait").hide();
}

function rank_date(){
    var p = new Promise(function(resolve, reject){
        show_spinner();          //做一些异步操作
        resolve(setTimeout(true_rank, 1000));
    });    
}

function true_rank(){
    var table_data = getTableData();
    // 设置默认降序
    if(query_date_sort == 0){
        query_date_sort = 1;
        $("th#registration svg use").attr("xlink:href", "#iconpaixu-xia");
        table_data.sort(compare("date", 1));
    }
    else if(query_date_sort == 1){
        query_date_sort = -1;
        $("th#registration svg use").attr("xlink:href", "#iconpaixu-shang");
        table_data.sort(compare("date", -1));
    }
    else{
        query_date_sort = 1;
        $("th#registration svg use").attr("xlink:href", "#iconpaixu-xia");
        table_data.sort(compare("date", 1));
    }

    // 网页更新排序的数据
    updateTable(table_data);
}