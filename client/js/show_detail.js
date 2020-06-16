var parent = window.opener;          // 获取打开页面的引用
var detail_data = parent.show_detail_data; 
var instruments_keys = parent.query_keys;
var instruments_names = ["ID", "案号", "标题", "文书类别", "案由", "承办部门", "级别", "结案日期", "Content"];
var data1_keys = parent.data1_keys;
var data1_names = ["ID", "姓名", "案号", "年龄", "性别", "身份证", "法人", "执行法院", "省份", "执行依据文号", "立案时间" , "执行依据单位", "义务", "履行情况", "履行部分", "未履行部分", "行为具体情形", "发布时间", "qysler"];
var data2_keys = parent.data2_keys;
var data2_names = ["案号", "被执行人", "被执行人地址", "被执行标的金额（元）", "申请执行人", "承办法院、联系电话"];

if(detail_data.type == "data1"){
    create_table();
    insert_data(data1_keys, data1_names);
}
else if(detail_data.type == "data2"){
    create_table();
    insert_data(data2_keys, data2_names);
}
else{
    create_table();
    insert_data(instruments_keys, instruments_names);
}

function create_table(){
    $("#detail-table tr").remove();    // 清除表格内容
    var table = $("#detail-table");
    table.html("<tr>\
                        <th width='10%'>字段</th>\
                        <th width='80%'>内容</th>\
                </tr>");
}

function insert_data(keys, names){
    $("#detail-table  tr:not(:first)").remove();      // 删去除表头之外的数据
    // 新建单元格
    for(var i = 1; i <= keys.length; i++){
        var insertTr = document.getElementById("detail-table").insertRow(i);
        for(var j = 0; j < 2; j++){
            insertTr.insertCell(j);
        }
    }
    // 写入新数据
    for(var i = 0; i < keys.length; i++){
        $("#detail-table tr:eq(" + (i + 1) + ") td:nth-child(1)").html(names[i]);
        $("#detail-table tr:eq(" + (i + 1) + ") td:nth-child(2)").html(detail_data[keys[i]]);
    }
}


