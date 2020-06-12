function create_query_table(){
    $("#result-table tr").remove();    // 清除表格内容
    var table = $("#result-table");
    table.html("<tr>\
                    <th width='10%'>ID</th>\
                    <th width='15%'>案号</th>\
                    <th width='10%'>标题</th>\
                    <th width='6%'>文书类别</th>\
                    <th width='10%'>案由</th>\
                    <th width='10%'>承办部门</th>\
                    <th width='5%'>级别</th>\
                    <th width='10%' id='registration' onclick='rank_registration()'>结案日期&nbsp;<svg class='icon sort-icon' aria-hidden='true'><use xlink:href='#iconpaixu'></use></svg></th>\
                    <th width='24%'>Content</th>\
                </tr>");
}

function insert_data(table_data, start, end){
    $("#result-table  tr:not(:first)").remove();      // 删去除表头之外的数据
    // 新建单元格
    for(var i = 1; i <= (end - start + 1); i++){
        var insertTr = document.getElementById("result-table").insertRow(i);
        insertTr.className = "multi";  
        for(var j = 0; j < 9; j++){
            insertTr.insertCell(j);
        }
    }
    // 写入新数据
    for(var i = 0; i <= (end - start); i++){
        for(var j = 0; j < 9; j++){
            $("#result-table tr:eq(" + (i + 1) + ") td:nth-child(" + (j + 1) + ")").html(table_data[start + i][j + 1]);
        }
    }
}


function Query_search(Observer){
    var query_search = {};

    query_search.onMessage = function(message, data, from){
        if(message == "Query"){
            if(from == Init){
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
                        insert_data(data, 0, 19);
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