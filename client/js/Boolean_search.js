function Boolean_search(Observer){
    var boolean_search = {};
    
    boolean_search.onMessage = function(message, data, from){
        if(message == "Boolean"){
            if(from == Init){
                let obj = {};
                obj.value = JSON.stringify(data);
                $.ajax({
                    type: 'GET',
                    url: 'Boolean_search',
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

    Observer.addView(boolean_search);
    return boolean_search;
}