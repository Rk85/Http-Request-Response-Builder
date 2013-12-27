import select, socket
import logging

logger = logging.getLogger()

def creat_socket():
	"""
		description: Creats new socket and returns it to make 
				new connection
		
		param:
		type:
		
		rparam: New Socket to process
		rtype: socket
		
		sample output: new_socket
	"""
	
	new_socket = 0
	try:
		new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		new_socket.setblocking(0)
		new_socket.settimeout(60)
	except Exception as e:
		logger.exception("Unable to create the socket : " + str(e))
		raise
	return new_socket

def create_epoll():
	""""
		description: Creats the Epoll listener for socket events
		
		param:
		type:
		
		rparam: epoll listener bucket for the socket
		rtype: epoll
		
		sample output: epoll
	"""
	
	try:
		epoll = select.epoll()
	except Exception as e:
		logger.exception("Unable to create Epoll Listener\n" +  str(e))
		raise
	return epoll

def register_socket_epoll_event(epoll, event_socket, event):
	"""
		description: Register the socket for the specified EPOLL event
		
		param: epoll - epoll listener bucket for sockets
		type: epoll
		param: event_socket - Socket to which the event should 
					be registered
		type: int
		param: event - Event that should be registered
		type: event instance
		
		rparam: 
		rtype:
		
		sample output: None
	"""
	
	try:
		epoll.register(event_socket, event)
	except Exception as e:
		logger.exception("Unable to register the socket fo the event" + event + " :" + str(e))
		raise

def modify_socket_epoll_event(epoll, event_socket, event):
	"""
		description: Modifies the socket for the specified EPOLL event
		
		param: epoll - epoll listener bucket for sockets
		type: epoll
		param: event_socket - Socket to which the event should 
					be modified
		type: int
		param: event - Event that should be modified
		type: event instance
		
		rparam: 
		rtype:
		
		sample output: None
	"""

	try:
		epoll.modify(event_socket, event)
	except Exception as e:
		logger.exception("Unable to modify the socket fo the event" + event + " :" + str(e))
		raise

def close_socket(epoll, socket_no, connections):
	"""
		description: Closes the given socket and removes its entry from
				global connections info dictionary
		
		param: epoll - epoll listener bucket for sockets
		type: epoll
		param: event_socket - Closing socket Id
		type: int
		param: connections - Global Connections Dictionary
		type: Dict
		
		rparam:
		rtype:
		
		sample output: None
	"""
	
	try:
		epoll.unregister(socket_no)
		connections[socket_no]['socket'].close()
		del connections[socket_no]
	except Exception as e:
		logger.exception("Error while closing the scoket : " + str(e))
		raise

def read_data(read_socket, read_size=1024):
	"""
		description: Reads the data from the given connection
		
		param: read_socket - Socket to read the data
		type: socket
		param: read_size - no of bytes should be received in 
					single read
		type: int
		
		rparam: data - strings that was read 
		rtype: string
	"""
	data = b''
	try:
		data = read_socket.recv(read_size)
	except Exception as e:
		logger.exception("Error While reading data from connection : " + str(e))
		return None
	return data.decode()

def send_data(send_socket, data):
	"""
		description: writes the data in the given connection
		
		param: send_socket - Socket to write the data
		type: socket
		param: data - Data that should be written in the socket
		type: string
		
		rparam: written_bytes - no of bytes written in the socket
		rtype: int

	"""
	
	try:
		written_bytes =	send_socket.send(bytes(data, 'utf-8'))
	except Exception as e:
		logger.exception("Error Happened while sending the data, so closing the connection\n" + str(e))
		return 0
	return written_bytes

def shut_down_socket(closing_socket):
	"""
		description: closes the socket gracefully
		
		param: closing_socket - Socket to shut down
		type: socket
		
		rparam: 
		rtype: 

	"""
	
	try:
		closing_socket.shutdown(socket.SHUT_RDWR)
	except Exception as e:
		logger.exception("Error Happened while shutting down the socket \n" + str(e))
		raise
