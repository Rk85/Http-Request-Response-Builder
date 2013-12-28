from ..shared.network_functions import modify_socket_epoll_event
from db_tables.db_base import session
from db_tables.http_tests import HttpTest
import datetime
import socket
import time
import logging

logger = logging.getLogger()

def handle_client_timer(client_connections_info, epoll, test_id, idle_time_out=60):
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
		try:
			now = datetime.datetime.now()	
			for fileno in client_connections_info.keys():
				if int((now-client_connections_info[fileno]['last_accessed_time']).total_seconds()) >= idle_time_out:
					logger.warning("Timout reached for the socket in client side " + str(fileno))
					modify_socket_epoll_event(epoll, fileno, 0)
					client_connections_info[fileno]['socket'].shutdown(socket.SHUT_RDWR)
			test = session.query(HttpTest).get(test_id)
			if test and test.completed:
				logger.debug("Test completed, so exiting the timer thread : Test ID : " + str(test_id) ) 
				break
			time.sleep(int(idle_time_out/2))
		except Exception as e:
			logger.exception(" Error in Client Time Thread : " + str(e) )
			raise
