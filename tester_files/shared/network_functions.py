import select, socket
import logging

logger = logging.getLogger()

def creat_socket():
    """
        Description : Creats new socket and returns it to make 
                new connection
        
        input_param :
        input_type :
        
        out_param : New Socket to process
        out_type: socket
        
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
        Description : Creats the Epoll listener for socket events
        
        input_param :
        input_type :
        
        out_param : epoll listener bucket for the socket
        out_type: epoll
        
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
        Description : Register the socket for the specified EPOLL event
        
        input_param : epoll - epoll listener bucket for sockets
        input_type : epoll
        input_param : event_socket - Socket to which the event should 
                    be registered
        input_type : int
        input_param : event - Event that should be registered
        input_type : event instance
        
        out_param : 
        out_type:
        
        sample output: None
    """
    
    try:
        epoll.register(event_socket, event)
    except Exception as e:
        logger.exception("Unable to register the socket fo the event" + event + " :" + str(e))
        raise

def modify_socket_epoll_event(epoll, event_socket, event):
    """
        Description : Modifies the socket for the specified EPOLL event
        
        input_param : epoll - epoll listener bucket for sockets
        input_type : epoll
        input_param : event_socket - Socket to which the event should 
                    be modified
        input_type : int
        input_param : event - Event that should be modified
        input_type : event instance
        
        out_param : 
        out_type:
        
        sample output: None
    """

    try:
        epoll.modify(event_socket, event)
    except Exception as e:
        logger.exception("Unable to modify the socket fo the event" + event + " :" + str(e))
        raise

def close_socket(epoll, socket_no, connections):
    """
        Description : Closes the given socket and removes its entry from
                global connections info dictionary
        
        input_param : epoll - epoll listener bucket for sockets
        input_type : epoll
        input_param : event_socket - Closing socket Id
        input_type : int
        input_param : connections - Global Connections Dictionary
        input_type : Dict
        
        out_param :
        out_type:
        
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
        Description : Reads the data from the given connection
        
        input_param : read_socket - Socket to read the data
        input_type : socket
        input_param : read_size - no of bytes should be received in 
                    single read
        input_type : int
        
        out_param : data - strings that was read 
        out_type: string
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
        Description : writes the data in the given connection
        
        input_param : send_socket - Socket to write the data
        input_type : socket
        input_param : data - Data that should be written in the socket
        input_type : string
        
        out_param : written_bytes - no of bytes written in the socket
        out_type: int

    """
    
    try:
        written_bytes =    send_socket.send(bytes(data, 'utf-8'))
    except Exception as e:
        logger.exception("Error Happened while sending the data, so closing the connection\n" + str(e))
        return 0
    return written_bytes

def shut_down_socket(closing_socket):
    """
        Description : closes the socket gracefully
        
        input_param : closing_socket - Socket to shut down
        input_type : socket
        
        out_param : 
        out_type: 

    """
    
    try:
        closing_socket.shutdown(socket.SHUT_RDWR)
    except Exception as e:
        logger.exception("Error Happened while shutting down the socket \n" + str(e))
        raise

def connect_with_server(socket, server_ip, server_port=80):
    """
        Description : Connects the Socket with the server end
        
        input_param : socket - Client side socket to make connection
        input_type : socket
        
        out_param :
        out_type:
        
        sample output:

    """
    try:
        socket.connect((server_ip, server_port))
    except:
        logger.error("Unable to make connection with the server")
        raise

