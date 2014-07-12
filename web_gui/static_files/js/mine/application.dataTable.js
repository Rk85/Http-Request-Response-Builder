(function(dataTable, $, undefined){
	dataTable.Init = function Init(table_id, options, filterRequired){
		var oTable = $(table_id).dataTable(options)
		if ( filterRequired === true ) {
			var thead=$(table_id).children("thead:first");
			var totalColumns = $(table_id + " tr:first").children("th").length;
			
			filters = '<tr>';
			for ( var i=0; i<totalColumns; i++){
				filters = filters + '<th><input class="input-small"/></th>';
			}
			filters = filters + '</tr>'
			
		    $(filters).appendTo(thead)
			
		    $(table_id + " thead input").keyup( function () {
		        /* Filter on the column (the index) of this element */
		        oTable.fnFilter( this.value, $(table_id + " thead input").index(this) );
		    } );
		}
	    $(".fg-toolbar").remove();
	
	};
	
	dataTable.filterEvent = function filterEvent(table_id, value, options){
        if (value == '') {
                 $(table_id + " tbody > tr").show();
        }
        else {
				var maxRows = options.maxRows || 0
        	    $(table_id + " > tbody > tr").hide();
	            var filters = value.split(',');
                $.map(filters, function(filter){
					if (filter != "") {
            			var searchRow = $(table_id + " td.search-col:contains-ci('" + filter + "')").parent("tr");
			            for( var i=1; i<= maxRows; i++){
                			searchRow.show();
			                searchRow = searchRow.next();
            			}
			        }
				});
             }
	}
	$.extend($.expr[":"], {
        "contains-ci": function (elem, i, match, array) {
            var elementValue = elem.textContent || elem.innerText || $(elem).text() || "";
            return elementValue.toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
         }
    });
}(Application.namespace("Application.dataTable"), jQuery));
