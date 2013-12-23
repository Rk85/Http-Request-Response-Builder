from ..shared.network_functions import modify_socket_epoll_event, shut_down_socket
import datetime
import socket
import time


def handle_server_timer(server_connections_info, epoll, idle_time_out):
	"""
		description: Handles the Server sockets timer. 
					when the socket in idle for some duration
					then closes that socket

		param:
		type:

		rparam:
		rtype:
		
		sample output:

	"""
	while True:
		now = datetime.datetime.now()	
		for fileno in server_connections_info.keys():
			if int((now-server_connections_info[fileno]['last_accessed_time']).total_seconds()) >= idle_time_out:
				print("Timout reached for the socket id " + str(fileno))
				modify_socket_epoll_event(epoll, fileno, 0)
				shut_down_socket(server_connections_info[fileno]['socket'])
		time.sleep(int(idle_time_out/2))
