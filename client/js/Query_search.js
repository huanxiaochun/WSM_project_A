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