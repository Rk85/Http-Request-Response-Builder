#!/usr/bin/python
import socket, select
import time
from configs.client_config import *
from ..shared.network_functions import *
from models.client_db_access import get_next_request
from models.new_test_insert import load_tests
from ..shared.client_http import *
import datetime
import logging
from .client_timer import handle_client_timer
import threading

logger = logging.getLogger(__name__)

class HTTPClientTimer(threading.Thread):
	"""
		HTTP Client Socket Timer Thread for Compliance Testing
	"""
	def __init__(self, client_connections_info, epoll, idle_time_out):
		threading.Thread.__init__(self)
		self.client_connections_info = client_connections_info
		self.epoll = epoll
		self.idle_time_out = idle_time_out

	def run(self):
		"""
			description: Runs the Client Socket Timer Thread
			
			param:
			type:
			
			rparam:
			rtype:
			
			sample output:
		"""
		logger.debug("Starting the Client Timer Thread")
		handle_client_timer(self.client_connections_info, self.epoll, self.idle_time_out)


def handle_client_socket_events(test_id, epoll, client_connections_info, client_requests, client_responses):
	"""
		description: Handles all the events happens in client side sockets
		
		param: epoll - Epoll listener bucket for the client socket
		type: epoll
		
		rparam:
		rtype:
		
		sample output: None
	"""
	try:
		while True:
			events = epoll.poll(PARALLEL_CLIENTS)
			for fileno, event in events:
				conn_info = client_connections_info[fileno]
				resp_info = client_responses[fileno]
				req_info = client_requests[fileno]
				conn_info['last_accessed_time'] = datetime.datetime.now()
				if event & select.EPOLLERR:
					print("EPOLL ERROR")
				if event & select.EPOLLIN:
					new_data = None
					read_err = None
					if resp_info['resp_start'] or resp_info['rem_bytes_to_read']:
						new_data = read_data(client_connections_info[fileno]['socket'])
						if not new_data:
							print("Read failed so cloing the socket\n")
							read_err = True
							resp_info['rem_bytes_to_read'] = 1
							modify_socket_epoll_event(epoll, fileno, 0)
							shut_down_socket(conn_info['socket'])
						if new_data and not resp_info.get('full_header_received'):
							resp_info['resp_start'] = False
							resp_info['header_data'] = resp_info['header_data'] + new_data
							if resp_info['header_data'].find(EOL1) != -1 or resp_info['header_data'].find(EOL2) != -1:
								print("Full Header Received\n")
								client_responses[fileno] = handle_server_response_data(resp_info)
								resp_info = client_responses[fileno]
								resp_info['full_header_received'] = True
						elif new_data and resp_info.get('full_header_received') and not resp_info['is_chunked']:
							resp_info['received_bytes'] = resp_info['received_bytes'] + len(new_data)
							resp_info['rem_bytes_to_read'] = resp_info['rem_bytes_to_read'] - len(new_data)
							resp_info['data'] = resp_info['data'] + new_data
					if not resp_info['rem_bytes_to_read'] and not read_err:
						print('-'*40 + '\n' + resp_info['header_data'])
						print(resp_info['data'])
						verify_server_response(req_info, resp_info)
						if resp_info['not_persistent']:
							print("Not Persistent Connection, So closing it\n")
							modify_socket_epoll_event(epoll, fileno, 0)
							shut_down_socket(conn_info['socket'])
						else:
							if conn_info['remaining_requests']:
								print("Starting new request in persistent connection\n")
								modify_socket_epoll_event(epoll, fileno, select.EPOLLOUT)
								conn_info['remaining_requests'] = conn_info['remaining_requests'] - 1
								client_requests[fileno] = intialize_client_request_info(get_next_request(test_id))
								client_responses[fileno] = intialize_client_response_info()
							else:
								print("Request Limit reached in Persistent connection\n")
								modify_socket_epoll_event(epoll, fileno, 0)
								shut_down_socket(conn_info['socket'])
				elif event & select.EPOLLOUT:
					if req_info.get('rem_bytes_to_send'):
						tot_sent = req_info['sent_bytes']
						tot_sent = tot_sent + send_data(conn_info['socket'], req_info['request_data'][tot_sent:])
						req_info['sent_bytes'] = tot_sent
						req_info['rem_bytes_to_send'] = req_info['tot_bytes_to_send'] - req_info['sent_bytes']
					else:
						modify_socket_epoll_event(epoll, fileno, select.EPOLLIN)
				elif event & select.EPOLLHUP:
					print("EPOLLHUP from client\n")
					if conn_info['remaining_requests']:
						client_socket = creat_socket()
						new_client_no = client_socket.fileno()
						client_connections_info[new_client_no] = {'socket': client_socket, 
															'tot_requests_per_connection': client_connections_info[fileno]['tot_requests_per_connection'],
															'remaining_requests': client_connections_info[fileno]['remaining_requests'],
															'last_accessed_time' : datetime.datetime.now()
															}
						client_requests[new_client_no] = intialize_client_request_info(get_next_request(test_id)) # change the 1 to category id
						client_responses[new_client_no] = intialize_client_response_info()
						connect_with_server(client_connections_info[new_client_no]['socket'])
						register_socket_epoll_event(epoll,new_client_no, select.EPOLLOUT)
						client_connections_info[new_client_no]['remaining_requests'] = client_connections_info[new_client_no]['remaining_requests'] - 1
					close_socket(epoll, fileno, client_connections_info)
					del client_requests[fileno]
					del client_responses[fileno]
	except:
		epoll.close()
		raise

def connect_with_server(socket):
	"""
		description: Connects the Socket with the server end
		
		param: socket - Client side socket to make connection
		type: socket
		
		rparam:
		rtype:
		
		sample output:
	"""

	try:
		socket.connect((SERVER_HOST, SERVER_PORT))
	except:
		print("Unable to make connection with the server")
		raise

def start_http_clients():
	"""
		description: Client HTTP Test start function
		
		param:
		type:
		
		rparam:
		rtype:
		
		sample output: 
	"""
	test_id = load_tests(category_id=1)
	client_connections_info = {}
	client_requests = {}
	client_responses = {}
	epoll = create_epoll()

	tot_requests_per_client = int(TOT_REQUESTS / PARALLEL_CLIENTS)
	for i in range(0,PARALLEL_CLIENTS):
		client_socket = creat_socket()
		client_connections_info[client_socket.fileno()] = {'socket': client_socket, 
															'tot_requests_per_connection': tot_requests_per_client,
															'remaining_requests': tot_requests_per_client,
															'last_accessed_time' : datetime.datetime.now()
															}
		client_requests[client_socket.fileno()] = intialize_client_request_info( get_next_request(test_id)  )
		client_responses[client_socket.fileno()] = intialize_client_response_info()
	for fileno in client_connections_info.keys():
		connect_with_server(client_connections_info[fileno]['socket'])
	for fileno in client_connections_info.keys():
		register_socket_epoll_event(epoll,fileno, select.EPOLLOUT)
		client_connections_info[fileno]['remaining_requests'] = client_connections_info[fileno]['remaining_requests'] - 1
	
	# Start the client timer thread
	http_client_timer = HTTPClientTimer(client_connections_info, epoll, idle_time_out=60)
	http_client_timer.start()
	handle_client_socket_events(test_id, epoll, client_connections_info, client_requests, client_responses)
	
	# Wait for timer thread to complete
	http_client_timer.join()
