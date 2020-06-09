function Observer() {
    var observer = {};
    var viewList = [];

    observer.addView = function(view) {
        viewList.push(view);
    }
    observer.fireEvent = function(message, data, from) {
        viewList.forEach(function(view) {
            if (view.hasOwnProperty('onMessage')) {
                view.onMessage(message, data, from);
            }
        })
    }
    return observer;
}

var obs = Observer();
var boolean_search = Boolean_search(obs);
var tolerant_search = Tolerant_search(obs);
var query_search = Query_search(obs);
var init = Init(obs);
