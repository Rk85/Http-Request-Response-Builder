This application tests a particular http server/proxy against the various configured http request categories. 
The user can configure any number of http request and group them under one or more category and test particular server against these categories.
They can automate the test cases also through the UI itself and schedule them against the server at different point in time

Requirement:
	It requires any sql db server as the data storage ( mysql is preferred )
	pymysql is required if you run the program with python version 3 or more than 3

To populate the initial data into the DB.Configure the correct db credential informations the file db_tables/db_base.py and run the following python file.
	* cd db_static_data
	* python insert_data.py

If everything goes well, do the following steps to start the servers

To start the Servers:
	Start the test running server as follows
		* cd Http-Request-Response-Builder/tester_files/server/
		* nohup sudo python server.py &
	
	Start the we gui server as follows
		* nohup sudo python web_gui_server.py &

open the following URL in web browser
	http://127.0.0.1:5000/

That's it. Now you can configure any kind of http request and can test them against any server or proxy.
