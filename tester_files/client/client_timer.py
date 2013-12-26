from ..shared.network_functions import modify_socket_epoll_event
import datetime
import socket
import time
#from settings import logger
#import logging

#logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

#logger.debug("TEST TIMER")
def handle_client_timer(client_connections_info, epoll, idle_time_out=60):
	"""
		description: Handles the client sockets timer. 
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
		for fileno in client_connections_info.keys():
			if int((now-client_connections_info[fileno]['last_accessed_time']).total_seconds()) >= idle_time_out:
				logger.warning("Timout reached for the socket in client side " + str(fileno))
				modify_socket_epoll_event(epoll, fileno, 0)
				client_connections_info[fileno]['socket'].shutdown(socket.SHUT_RDWR)
		time.sleep(int(idle_time_out/2))
