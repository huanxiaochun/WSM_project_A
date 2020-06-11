function create_query_table(){
    var table = $("#result-table");
    table.html("<tr>\
                    <th id='amount' onclick='rank_amount()'>ID&nbsp;<svg class='icon sort-icon' aria-hidden='true'><use xlink:href='#iconpaixu'></use></svg></th>\
                    <th>案号</th>\
                    <th>标题</th>\
                    <th>文书类别</th>\
                    <th>案由</th>\
                    <th>承办部门</th>\
                    <th>级别</th>\
                    <th id='registration' onclick='rank_registration()'>结案日期&nbsp;<svg class='icon sort-icon' aria-hidden='true'><use xlink:href='#iconpaixu'></use></svg></th>\
                    <th width='20%'>Content</th>\
                </tr>")
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
                        console.log(evt_data);
                        create_query_table();
                        // TODO
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