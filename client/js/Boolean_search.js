// 0: unsorted    1: Descending order   -1: Ascending order
var boolean_Filing_date_sort = 0;
var boolean_release_date_sort = 0;
var boolean_imoney_sort = 0;
var data1_keys = ["ID", "iname", "caseCode", "age", "sexy", "cardNum", "businessEntity", "courtName", "areaName",
                "gistId", "regDate", "gistUnit", "duty", "performance", "performedPart", "unperformPart", "disruptTypeName",
                "publishDate", "qysler"];
var data2_keys = ["caseCode", "iname", "iaddress", "imoney", "ename", "courtName_phone"];


function Boolean_search(Observer){
    var boolean_search = {};
    
    boolean_search.onMessage = function(message, data, from){
        if(message == "Boolean"){
            if(from == Init){
                $("#query-list").hide();
                
                let obj = {};
                obj.value = JSON.stringify(data);
                $.ajax({
                    type: 'GET',
                    url: 'Boolean_search',
                    data: obj,
                    dataType: 'json',
                    success: function(evt_data) {
                        var data = evt_data.result;

                        var height = $('#result-border').height();
                        if(data["data1"].length > 0 && data["data2"].length > 0){
                            $("#data1-list").show();
                            $("#data2-list").show();
                            $("#data1-list").css('top',0);
                            $("#data1-list").css('height', height/2);
                            $("#data2-list").css('top', height/2);
                            $("#data2-list").css('height', height/2);
                            
                            create_boolean_table1();
                            var data1 = data["data1"];
                            insert_data1(data1, 0, data1.length - 1);
                            
                            create_boolean_table2()
                            var data2 = data["data2"];
                            insert_data2(data2, 0, data2.length - 1);
                        }
                        else if(data["data1"].length > 0 && data["data2"].length == 0){
                            $("#data1-list").show();
                            $("#data2-list").hide();
                            $("#data1-list").css('top',0);
                            $("#data1-list").css('height', height);

                            // 创建表格
                            create_boolean_table1();
                            // 插入前20个数据
                            var data1 = data["data1"];
                            insert_data1(data1, 0, data1.length - 1);
                        }
                        else if(data["data1"].length == 0 && data["data2"].length > 0){
                            $("#data2-list").show();
                            $("#data1-list").hide();
                            $("#data2-list").css('top',0);
                            $("#data2-list").css('height', height);

                            // 创建表格
                            create_boolean_table2();
                            // 插入前20个数据
                            var data2 = data["data2"];
                            insert_data2(data2, 0, data2.length - 1);
                        }
                        
                        $("#result_wait").hide();
                    },
                    error: function(jqXHR) {
                        console.log('post error!!', jqXHR);
                    },
                });
            }
        }
    }

    Observer.addView(boolean_search);
    return boolean_search;
}

function create_boolean_table1(){
    $("#data1-table tr").remove();    // 清除表格内容
    var table = $("#data1-table");
    table.html("<tr>\
                    <th width='7%'>ID</th>\
                    <th width='4%'>姓名</th>\
                    <th width='5%'>案号</th>\
                    <th width='3%'>年龄</th>\
                    <th width='3%'>性别</th>\
                    <th width='5%'>身份证</th>\
                    <th width='3%'>法人</th>\
                    <th width='5%'>执行法院</th>\
                    <th width='4%'>省份</th>\
                    <th width='4%'>执行依据文号</th>\
                    <th width='8%' id='Filing_date' onclick='rank_Filing_date()'>立案时间&nbsp;<svg class='icon sort-icon' aria-hidden='true'><use xlink:href='#iconpaixu'></use></svg></th>\
                    <th width='4%'>执行依据单位</th>\
                    <th width='5%'>义务</th>\
                    <th width='5%'>履行情况</th>\
                    <th width='3%'>履行部分</th>\
                    <th width='4%'>未履行部分</th>\
                    <th width='4%'>行为具体情形</th>\
                    <th width='8%' id='release_date' onclick='rank_release_date()'>发布时间&nbsp;<svg class='icon sort-icon' aria-hidden='true'><use xlink:href='#iconpaixu'></use></svg></th>\
                    <th width='5%'>qysler</th>\
                </tr>");
}

function insert_data1(table_data, start, end){
    $("#data1-table  tr:not(:first)").remove();      // 删去除表头之外的数据
    // 新建单元格
    for(var i = 1; i <= (end - start + 1); i++){
        var insertTr = document.getElementById("data1-table").insertRow(i);
        for(var j = 0; j < 19; j++){
            var insertTd = insertTr.insertCell(j);
            insertTd.onclick = function() { alert($(this).text()) };
        }
    }
    // 写入新数据
    for(var i = 0; i <= (end - start); i++){
        for(var j = 0; j < 21; j++){
            // ignore partyTypeName
            if(j < 10){
                $("#data1-table tr:eq(" + (i + 1) + ") td:nth-child(" + (j + 1) + ")").html(table_data[start + i][j + 1]);
            }
            else if(j == 10){
                continue;
            }
            else{
                $("#data1-table tr:eq(" + (i + 1) + ") td:nth-child(" + j + ")").html(table_data[start + i][j + 1]);
            }            
        }
    }
}

function create_boolean_table2(){
    $("#data2-table tr").remove();    // 清除表格内容
    var table = $("#data2-table");
    table.html("<tr>\
                    <th width='10%'>案号</th>\
                    <th width='5%'>被执行人</th>\
                    <th width='20%'>被执行人地址</th>\
                    <th width='10%' id='imoney' onclick='rank_imoney()'>被执行标的金额（元）&nbsp;<svg class='icon sort-icon' aria-hidden='true'><use xlink:href='#iconpaixu'></use></svg></th>\
                    <th width='5%'>申请执行人</th>\
                    <th width='20%'>承办法院、联系电话</th>\
                </tr>");
}

function insert_data2(table_data, start, end){
    $("#data2-table  tr:not(:first)").remove();      // 删去除表头之外的数据
    // 新建单元格
    for(var i = 1; i <= (end - start + 1); i++){
        var insertTr = document.getElementById("data2-table").insertRow(i);
        for(var j = 0; j < 6; j++){
            var insertTd = insertTr.insertCell(j);
            insertTd.onclick = function() { alert($(this).text()) };
        }
    }
    // 写入新数据
    for(var i = 0; i <= (end - start); i++){
        for(var i = 0; i <= (end - start); i++){
            for(var j = 0; j < 6; j++){
                $("#data2-table tr:eq(" + (i + 1) + ") td:nth-child(" + (j + 1) + ")").html(table_data[start + i][j + 1]);
            }
        }
    }
}

// rank regdate
function getTableData1(){
    var result = new Array();
    $("#data1-table").find("tr").each(function(){
        var tmp = new Array();
        $(this).find("td").each(function(){
            tmp.push($(this).text());
        })
        // 不是th的值
        if(tmp.length != 0){
            result.push({
                "ID": tmp[0],
                "iname": tmp[1],
                "caseCode": tmp[2],
                "age": tmp[3],
                "sexy": tmp[4],
                "cardNum": tmp[5],
                "businessEntity": tmp[6],
                "courtName": tmp[7],
                "areaName": tmp[8],
                "gistId": tmp[9],
                "regDate": tmp[10],
                "gistUnit": tmp[11],
                "duty": tmp[12],
                "performance": tmp[13],
                "performedPart": tmp[14],
                "unperformPart": tmp[15],
                "disruptTypeName": tmp[16],
                "publishDate": tmp[17],
                "qysler": tmp[18]
            })
        }
    })
    return result;
}

function updateTableData1(table){
    $("#data1-table  tr:not(:first)").remove();      // 删去除表头之外的数据
    // 新建单元格
    for(var i = 1; i <= table.length; i++){
        var insertTr = document.getElementById("data1-table").insertRow(i);
        for(var j = 0; j < 19; j++){
            var insertTd = insertTr.insertCell(j);
            insertTd.onclick = function() { alert($(this).text()) };
        }
    }
    // 写入新数据
    for(var i = 0; i < table.length; i++){
        for(var j = 0; j < 19; j++){
            $("#data1-table tr:eq(" + (i + 1) + ") td:nth-child(" + (j + 1) + ")").html(table[i][data1_keys[j]]);
        }
    }

    $("#result_wait").hide();
}

function true_rank_Filing_date(){
    var table_data = getTableData1();

    // 设置默认降序
    if(boolean_Filing_date_sort == 0){
        boolean_Filing_date_sort = 1;
        $("th#Filing_date svg use").attr("xlink:href", "#iconpaixu-xia");
        table_data.sort(compare("regDate", 1));
    }
    else if(boolean_Filing_date_sort == 1){
        boolean_Filing_date_sort = -1;
        $("th#Filing_date svg use").attr("xlink:href", "#iconpaixu-shang");
        table_data.sort(compare("regDate", -1));
    }
    else{
        boolean_Filing_date_sort = 1;
        $("th#Filing_date svg use").attr("xlink:href", "#iconpaixu-xia");
        table_data.sort(compare("regDate", 1));
    }

    // 网页更新排序的数据
    updateTableData1(table_data);
}

function rank_Filing_date(){
    var p = new Promise(function(resolve, reject){
        show_spinner();          //做一些异步操作
        resolve(setTimeout(true_rank_Filing_date, 500));
    });    
}

// rank publishdate
function true_rank_release_date(){
    var table_data = getTableData1();

    // 设置默认降序
    if(boolean_release_date_sort == 0){
        boolean_release_date_sort = 1;
        $("th#release_date svg use").attr("xlink:href", "#iconpaixu-xia");
        table_data.sort(compare("publishDate", 1));
    }
    else if(boolean_release_date_sort == 1){
        boolean_release_date_sort = -1;
        $("th#release_date svg use").attr("xlink:href", "#iconpaixu-shang");
        table_data.sort(compare("publishDate", -1));
    }
    else{
        boolean_release_date_sort = 1;
        $("th#release_date svg use").attr("xlink:href", "#iconpaixu-xia");
        table_data.sort(compare("publishDate", 1));
    }

    // 网页更新排序的数据
    updateTableData1(table_data);
}

function rank_release_date(){
    var p = new Promise(function(resolve, reject){
        show_spinner();          //做一些异步操作
        resolve(setTimeout(true_rank_release_date, 500));
    });    
}

// rank imoney
function getTableData2(){
    var result = new Array();
    $("#data2-table").find("tr").each(function(){
        var tmp = new Array();
        $(this).find("td").each(function(){
            tmp.push($(this).text());
        })
        // 不是th的值
        if(tmp.length != 0){
            result.push({
                "caseCode": tmp[0],
                "iname": tmp[1],
                "iaddress": tmp[2],
                "imoney": tmp[3],
                "ename": tmp[4],
                "courtName_phone": tmp[5]
            })
        }
    })
    return result;
}

function updateTableData2(table){
    $("#data2-table  tr:not(:first)").remove();      // 删去除表头之外的数据
    // 新建单元格
    for(var i = 1; i <= table.length; i++){
        var insertTr = document.getElementById("data2-table").insertRow(i);
        for(var j = 0; j < 6; j++){
            var insertTd = insertTr.insertCell(j);
            insertTd.onclick = function() { alert($(this).text()) };
        }
    }
    // 写入新数据
    for(var i = 0; i < table.length; i++){
        for(var j = 0; j < 6; j++){
            $("#data2-table tr:eq(" + (i + 1) + ") td:nth-child(" + (j + 1) + ")").html(table[i][data2_keys[j]]);
        }
    }

    $("#result_wait").hide();
}

function true_rank_imoney(){
    var table_data = getTableData2();

    // 设置默认降序
    if(boolean_imoney_sort == 0){
        boolean_imoney_sort = 1;
        $("th#imoney svg use").attr("xlink:href", "#iconpaixu-xia");
        table_data.sort(compare("imoney", 1));
    }
    else if(boolean_imoney_sort == 1){
        boolean_imoney_sort = -1;
        $("th#imoney svg use").attr("xlink:href", "#iconpaixu-shang");
        table_data.sort(compare("imoney", -1));
    }
    else{
        boolean_imoney_sort = 1;
        $("th#imoney svg use").attr("xlink:href", "#iconpaixu-xia");
        table_data.sort(compare("imoney", 1));
    }

    // 网页更新排序的数据
    updateTableData2(table_data);
}

function rank_imoney(){
    var p = new Promise(function(resolve, reject){
        show_spinner();          //做一些异步操作
        resolve(setTimeout(true_rank_imoney, 500));
    });    
}