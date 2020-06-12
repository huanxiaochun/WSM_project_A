var ObserverCopy;
var opts = {            
    lines: 8, 
    length: 10, 
    width: 10,
    radius: 15, 
    corners: 1, 
    rotate: 0, 
    direction: 1, 
    color: '#90DC90', 
    opacity: 0.8,
    speed: 1, 
    trail: 60, 
    shadow: false, 
    hwaccel: false,          
    className: 'mySpin', 
    zIndex: 2e9,
    top: '50%',
    left: '50%'
};
var spinner = new Spinner(opts);

function Init(Observer){
    var init = {};
    ObserverCopy = Observer;

    $("#result_wait").hide();
    
    var mode = getParams("mode");
    var value = getParams("value");

    $("#search_input").val(value);
    $('#mode-select').val(mode);

    show_spinner();
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

function show_spinner(){
    $("#result_wait").show(function(){
        var target= document.getElementById('result_wait');
        spinner.spin(target);  
    });
}

function search_value(mode, value){
    show_spinner();
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
                var val1 = new Date(Date.parse(obj1[property].replace('年','-').replace('月','-').replace('日','')));
                var val2 = new Date(Date.parse(obj2[property].replace('年','-').replace('月','-').replace('日','')));
                return val2 - val1;
            }
        }
        else if(order == -1){
            return function(obj1, obj2){
                var val1 = new Date(Date.parse(obj1[property].replace('年','-').replace('月','-').replace('日','')));
                var val2 = new Date(Date.parse(obj2[property].replace('年','-').replace('月','-').replace('日','')));
                return val1 - val2;
            }
        }
    }
}

// function rank_amount(){
//     var table_data = getTableData();
//     // 设置默认降序
//     if(amount_sort == 0){
//         amount_sort = 1;
//         $("th#amount svg use").attr("xlink:href", "#iconpaixu-xia");
//         table_data.sort(compare("amount", 1));
//     }
//     else if(amount_sort == 1){
//         amount_sort = -1;
//         $("th#amount svg use").attr("xlink:href", "#iconpaixu-shang");
//         table_data.sort(compare("amount", -1));
//     }
//     else{
//         amount_sort = 1;
//         $("th#amount svg use").attr("xlink:href", "#iconpaixu-xia");
//         table_data.sort(compare("amount", 1));
//     }

//     // 网页更新排序的数据
//     updateTable(table_data);
// }


