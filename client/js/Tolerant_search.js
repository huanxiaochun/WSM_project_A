function Tolerant_search(Observer){
    var tolerant_search = {};

    tolerant_search.onMessage = function(message, data, from){
        if(message == "Tolerant"){
            if(from == Init){
                $("#query-list").hide();
                
                let obj = {};
                obj.value = JSON.stringify(data);
                $.ajax({
                    type: 'GET',
                    url: 'Tolerant_search',
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

    Observer.addView(tolerant_search);
    return tolerant_search;
}