var ObserverCopy;
function Init(Observer){
    var init = {};
    ObserverCopy = Observer;

    var mode = getParams("mode");
    var value = getParams("value");
    $("#search_input").val(value);

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
