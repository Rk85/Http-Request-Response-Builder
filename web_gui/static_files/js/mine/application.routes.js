var Application = window.Application || {};
Application.Routing = {
		Configure : function(){
			Application.Routing.Sammy = $.sammy("#main", function(){
				this.get("#main", function(context){
					context.log("MAIN");
					
				});
				this.get("#/test/new", function(context){
					context.log("#/test/new");
					var url = "/test/new"
					Application.Tab.addTab("Scheduling New Test" , url );
				});
				this.get("#/test/search", function(context){
					context.log("#/test/search");
					var url = "/test/search"
					Application.Tab.addTab("Test Search" , url );
				});
				this.get("#/test/details/:ID", function(context){
					var url = "/test/details/" + this.params['ID'];
					Application.Tab.addTab("TEST ID : " + this.params['ID'] , url );
					context.log("NEW");
				});
				this.get("#/test/details", function(context){
					context.log("#/test/details");
					var url = "/test/details"
					Application.Tab.addTab("Detail - All Tests" , url );
				});
				this.get("#/request/new", function(context){
					context.log("#/request/new");
					var url = "/request/new"
					Application.Tab.addTab("New Request/Response Config" , url );
				});
				this.get("#/request/details/:ID", function(context){
					var url = "/request/details/" + this.params['ID'];
					Application.Tab.addTab("Request ID : " + this.params['ID'] , url );
					context.log("NEW");
				});
				this.get("#/request/details", function(context){
					context.log("#/request/details");
					var url = "/request/details"
					Application.Tab.addTab("Detail - All Request" , url );
				});
				this.get("#/help", function(context){
					context.log("#/help");
					var url = "/help"
					Application.Tab.addTab("Help Page" , url, true);
				});

			});
		},
		run : function(){
			Application.Routing.Sammy.run("#main");
		}
}
