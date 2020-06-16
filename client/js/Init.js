var ObserverCopy;
var show_detail_data;
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

function Init(Observer){
    var init = {};
    ObserverCopy = Observer;

    $("#result_wait").hide();
    
    var mode = getParams("mode");
    var value = getParams("value");

    $("#search_input").val(value);
    $('#mode-select').val(mode);

    search_value(mode, value);

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
    // var width = $('#bottom-div').width();
    // var height = $('#bottom-div').height();

    // // $("#result_wait").css('left',0);
    // $("#result_wait").css('height', height);
    // $("#result_wait").css('width', width);
    $("#result_wait").empty();
    $("#result_wait").show(function(){
        var target= document.getElementById('result_wait');
        var spinner = new Spinner(opts);
        spinner.spin(target);  
    });
}

function search_value(mode, value){
    show_spinner();
    if(mode == "Boolean"){
        boolean_Filing_date_sort = 0;
        boolean_release_date_sort = 0;
        boolean_imoney_sort = 0;
        boolean_casecode_1_sort = 0;
        boolean_casecode_2_sort = 0;
        ObserverCopy.fireEvent("Boolean", value, Init);
    }
    else if(mode == "Tolerant"){
        tolerant_Filing_date_sort = 0;
        tolerant_release_date_sort = 0;
        tolerant_imoney_sort = 0;
        ObserverCopy.fireEvent("Tolerant", value, Init);
    }
    else{
        query_date_sort = 0;
        query_caseCode_sort = 0;
        ObserverCopy.fireEvent("Query", value, Init);
    }
}

var reg =/[\u4e00-\u9fa5]/g;
function deal_arr(arr){
    if(arr.length == 1){
        arr.push(0);
        arr.push(0);
    }
    else if(arr.length == 2){
        arr.splice(1, 0, 0);   // 在第二个位置插入0
    }
    return arr;
}

// 排序的比较函数 1: 降序  -1: 升序
function compare(property, order){
    if(property == "amount" || property == "imoney"){
        if(order == 1){
            return function(obj1, obj2){
                // 去除字符串中的中文
                var val1 = Number(obj1[property].replace(reg, ""));
                var val2 = Number(obj2[property].replace(reg, ""));
                return val2 - val1;
            }
        }
        else if(order == -1){
            return function(obj1, obj2){
                var val1 = Number(obj1[property].replace(reg, ""));
                var val2 = Number(obj2[property].replace(reg, ""));
                return val1 - val2;
            }
        }
    }
    else if(property == "date" || property == "regDate" || property == "publishDate"){
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
    else if(property == "caseCode"){
        if(order == 1){
            return function(obj1, obj2){
                var arr1 = obj1[property].match(/[0-9]+/g);  // 提取数字
                var arr2 = obj2[property].match(/[0-9]+/g);
                
                if(arr1.length < 3){
                    arr1 = deal_arr(arr1);
                }
                if(arr2.length < 3){
                    arr2 = deal_arr(arr2);
                }

                
                if(Number(arr2[0]) == Number(arr1[0])){
                    if(Number(arr2[1]) == Number(arr1[1])){
                        return Number(arr2[2]) - Number(arr1[2]);
                    }
                    else{
                        return Number(arr2[1]) - Number(arr1[1]);
                    }
                }
                else{
                    return Number(arr2[0]) - Number(arr1[0]);
                }
            }
        }
        else if(order == -1){
            return function(obj1, obj2){
                var arr1 = obj1[property].match(/\d+(.\d+)?/g);  // 提取数字
                var arr2 = obj2[property].match(/\d+(.\d+)?/g);

                if(arr1.length < 3){
                    arr1 = deal_arr(arr1);
                }
                if(arr2.length < 3){
                    arr2 = deal_arr(arr2);
                }

                if(Number(arr2[0]) == Number(arr1[0])){
                    if(Number(arr2[1]) == Number(arr1[1])){
                        return Number(arr1[2]) - Number(arr2[2]);
                    }
                    else{
                        return Number(arr1[1]) - Number(arr2[1]);
                    }
                }
                else{
                    return Number(arr1[0]) - Number(arr2[0]);
                }
            }
        }
    }
}
