(function(dataTable, $, undefined){
	dataTable.Init = function Init(table_id, options){
		var thead=$(table_id).children("thead:first");
		var oTable = $(table_id).dataTable(options)
		var totalColumns = $(table_id + " tr:first").children("th").length;
		
		filters = '<tr>';
		for ( var i=0; i<totalColumns; i++){
			filters = filters + '<th><input class="input-small"/></th>';
		}
		filters = filters + '</tr>'
		
	    $(filters).appendTo(thead)
		
	    $("thead input").keyup( function () {
	        /* Filter on the column (the index) of this element */
	        oTable.fnFilter( this.value, $("thead input").index(this) );
	    } );
	    $(".fg-toolbar").remove();
	
	}
}(Application.namespace("Application.dataTable"), jQuery));
