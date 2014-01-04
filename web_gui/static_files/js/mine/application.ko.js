ko.bindingHandlers.slideVisible = {
    init: function(element, valueAccessor) {
        var value = ko.utils.unwrapObservable(valueAccessor()); // Get the current value of the current property we're bound to
        $(element).toggle(value); // jQuery will hide/show the element depending on whether "value" or true or false
    },
    update: function(element, valueAccessor, allBindingsAccessor) {
        // First get the latest data that we're bound to
        var value = valueAccessor(), allBindings = allBindingsAccessor();
         
        // Next, whether or not the supplied model property is observable, get its current value
        var valueUnwrapped = ko.utils.unwrapObservable(value); 
         
        // Grab some more data from another binding property
        var duration = allBindings.slideDuration || 400; // 400ms is default duration unless otherwise specified
         
        // Now manipulate the DOM element
        if (valueUnwrapped == true) 
            $(element).slideDown(duration); // Make the element visible
        else
            $(element).slideUp(duration);   // Make the element invisible
    }
};


ko.bindingHandlers.options.preprocess = function(value, name, addBindingCallback) {
    alert(value);
    return  'value + ".toUpperCase()"';
}
function addBindingCallback()
{
alert("preprocess")
}
var origOptionsUpdate = ko.bindingHandlers.options.update;
ko.bindingHandlers.options.update = function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    var value =  ko.utils.unwrapObservable(valueAccessor());
    origOptionsUpdate.apply(this, arguments);
    var children=$(element).children();
    for(var i=0;i<children.length;i++){
        $(children[i]).attr( "data-bind", 'enable:true' );
    }
    

};
