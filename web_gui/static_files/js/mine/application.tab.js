(function(app, $, undefined){
var tabCounter = 0;
var tab_selecter = "#application_tabs";
var tab_url_index_mapper = {'#main' : 'newtab-0'};
app.Tab = {
	setup: function(){
		// Function called at the initialization of the web page
		mainTabs = $( tab_selecter  ).tabs({closable: true });
		$( tab_selecter ).delegate( "span.ui-icon-close", "click", function(e) {
			e.preventDefault();
			// Remove the Closing Tab and send its ID to our function
			app.Tab.closeTab( $(this).closest("li").remove().attr("aria-controls") );
		});
	},
	addTab : function(Title, url, htmlTextOnly) {
		   // This is called when ever we want to create a new tab
		   var tabs = $( tab_selecter  ).tabs();
		   var url_hash = "#" + url;
		   if (url_hash in tab_url_index_mapper){
			//If the page is already in open state, select the page.
			// Instead of creating the duplicate page for the same URL
			var index = $(tab_selecter + ' a[href=#' + tab_url_index_mapper[url_hash] + ']').parent().index(); 
			$(tab_selecter).tabs("option", "active", index);
			$(tab_selecter).tabs( "refresh" );
		   }
		   else{
			// If no previous tabs are present for the URL
			// Append the new created tab to global Tab list
			var ul = tabs.find( "ul" ).first();
			tabCounter  = tabCounter + 1;
			new_tab = "<li><a href='#newtab-" + tabCounter + "'>" + Title + "</a><span class='ui-icon ui-icon-close' role='presentation'>Remove Tab</span></li>"
			$( new_tab ).appendTo( ul );

			// Send the Ajax Request for the newly created tab
			$.ajax({
				url: url,
				success: function(data){
					new_tab_div = "<div id='newtab-" + tabCounter +"'></div>"
					tabs.append(new_tab_div);
					new_tab_id = "#newtab-" + tabCounter
					// Append the Ajax response as html data for the newly created Tab 
					var page_html = '<div class="row-fluid"> \
										<div data-bind="template: {name: \'menu_list\'}"> \
										</div> \
										<div class="content-section over-flow"> ' +  data.form + '\
										</div> \
									</div>'

					$( new_tab_id ).html(page_html);
					
					// Call the Knock out bindings for the newly created page
					if (htmlTextOnly === undefined || htmlTextOnly === false){
						applyFormBindings(data.response_data, new_tab_id);
					}
					if ( htmlTextOnly === true ){
						ko.applyBindings({}, $(new_tab_id)[0]);
					}

					// Make the last loaded tab as the active one
					$(tabs).tabs("option","active", -1 );
					
				}
			});
			// Once the tab is loaded, refresh the tab list
			tabs.tabs( "refresh" );
			// Add an entry in the Mapping dictionary
			tab_url_index_mapper[url_hash] = 'newtab-' + tabCounter;
			$(tab_selecter).on("tabsactivate", function(event, ui) { // select event
				selectedTabId = ui.newPanel.attr('id');
				for (var key in tab_url_index_mapper) {
					if (tab_url_index_mapper[key] == selectedTabId ){
						window.location.hash = key;
					}
				}
				//console.dir(ui);
				
 			 });
		}
	},
	closeTab : function(currentTabId){
		var prevTabId = $( "#" +currentTabId ).prev().attr("id");
		$( "#" + currentTabId ).remove();
		var index = $(tab_selecter + ' a[href=#' + prevTabId + ']').parent().index(); 
		$(tab_selecter).tabs("option", "active", index);
		$(tab_selecter).tabs( "refresh" );
		for (var key in tab_url_index_mapper) {
			if (tab_url_index_mapper[key] == currentTabId){
				delete tab_url_index_mapper[key];
			}
			else if (tab_url_index_mapper[key] == prevTabId){
				window.location.hash = key;
			}
			else{}
		}
	}
}
}(window.Application = window.Application || {}, jQuery));
