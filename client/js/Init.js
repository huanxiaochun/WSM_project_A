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
    var width = $('#bottom-div').width();
    var height = $('#bottom-div').height();

    $("#result_wait").css('left',0);
    $("#result_wait").css('height', height);
    $("#result_wait").css('width', width);

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

var reg =/[\u4e00-\u9fa5]/g;
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
}

// window.alert = alert;
// function alert(data) {
//     var a = document.createElement("div"),
//         p = document.createElement("p"),
//         btn = document.createElement("div"),
//         textNode = document.createTextNode(data ? data : ""),
//         btnText = document.createTextNode("确定");
//     // 控制样式
//     css(a, {
//         "position" : "absolute",
//         "left" : "0",
//         "right" : "0",
//         "top" : "20%",
//         "width" : "300px",
//         "margin" : "0 auto",
//         "background-color" : "#fff",
//         "font-size" : "12px",
//         "font-family": "Lucida Console",
//         "text-align" : "center"
//     });
//     css(btn, {
//         "background" : "#CEEFE0",
//         "font-size" : "12px",
//         "font-family": "Lucida Console",
//     })
//     // 内部结构套入
//     p.appendChild(textNode);
//     btn.appendChild(btnText);
//     a.appendChild(p);
//     a.appendChild(btn);
//     // 整体显示到页面内
//     document.getElementsByTagName("body")[0].appendChild(a);

//     // 确定绑定点击事件删除标签
//     btn.onclick = function() {
//         a.parentNode.removeChild(a);
//     }
// }
// function css(targetObj, cssObj) {
//     var str = targetObj.getAttribute("style") ? targetObj.getAttribute("style") : "";
//     for(var i in cssObj) {
//         str += i + ":" + cssObj[i] + ";";
//     }
//     targetObj.style.cssText = str;
// }
