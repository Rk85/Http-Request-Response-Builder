(function( app, $, undefined ) {
$(document).ajaxStart(function(){
   	 $('#loader').show();
    });
$(document).ajaxStop(function(){
   	 $('#loader').hide();
    });
app.namespace = function(ns){
	var parts = [];
	var parent = {};
	var i = 0;
	parts = ns.split(".");
	if(parts[0] == "Application"){
		parts = parts.slice(1, parts.length)
		parent = Application;
	}
	for(i = 0; i < parts.length; i++){
		if(parent[parts[i]] === undefined){
			parent[parts[i]] ={};
		}
		parent = parent[parts[i]];
	}
	return parent;
}  	
}( window.Application = window.Application || {}, jQuery ));