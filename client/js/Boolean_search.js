function Boolean_search(Observer){
    ObserverCopy = Observer;
    var boolean_search = {};

    Observer.addView(boolean_search);
    return boolean_search;
}