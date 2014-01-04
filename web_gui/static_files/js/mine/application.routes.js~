var Application = window.Application || {};
Application.Routing = {
		Configure : function(){
			Application.Routing.Sammy = $.sammy("#main", function(){
				this.get("#main", function(context){
					context.log("MAIN");
					
				});
				this.get("#/test/:ID", function(context){
					var url = "/scheduled_test/" + this.params['ID'];
					Application.Tab.addTab("TEST ID : " + this.params['ID'] , url );
					context.log("NEW");
				});
				this.get("#/schedule_new_test", function(context){
					context.log("#/schedule_new_test");
					var url = "/schedule_new_test"
					Application.Tab.addTab("Scheduling New Test" , url );
				});
				this.get("#/search_test", function(context){
					context.log("#/search_test");
					var url = "/search_test"
					Application.Tab.addTab("Test Search" , url );
				});
				this.get("#/report/all_test", function(context){
					context.log("#/report/all_test");
					var url = "/report/all_test"
					Application.Tab.addTab("Report - All Tests" , url );
				});
				this.get("#/report/running_test", function(context){
					context.log("#/report/running_test");
					var url = "/report/running_test"
					Application.Tab.addTab("Report - Running Tests" , url );
				});
				this.get("#/help", function(context){
					context.log("#/help");
					var url = "/help"
					Application.Tab.addTab("Help Page" , url );
				});

			});
		},
		run : function(){
			Application.Routing.Sammy.run("#main");
		}
}
