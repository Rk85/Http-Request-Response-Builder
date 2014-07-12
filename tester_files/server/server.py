#!/usr/bin/python3.2
import socket, select
from ..shared.network_functions import ( creat_socket,
    create_epoll,
    register_socket_epoll_event,
    modify_socket_epoll_event,
    close_socket,
    read_data,
    send_data,
    shut_down_socket
    )
from ..shared.server_http import ( intialize_server_request_info,
    intialize_server_response_info,
    handle_client_request_data,
    verify_client_request
    )
from configs.server_config import ( EOL1,
    EOL2,
    TOT_CLIENT
    )
import datetime
from models.server_db_access import get_response
from .server_timer import handle_server_timer
import threading
import logging

logger = logging.getLogger()


class HTTPServerTimer(threading.Thread):
    """
        Description : HTTP Server Socket Timer Thread to handle Http Timeouts
        
    """
    def __init__(self, server_connections_info, epoll, idle_time_out):
        threading.Thread.__init__(self)
        self.server_connections_info = server_connections_info
        self.epoll = epoll
        self.idle_time_out = idle_time_out

    def run(self):
        """
            Description: Runs the Server Socket Timer Thread
            
            input_param:
            input_type:
            
            out_param:
            out_type:
            
            sample output:
        """
        logger.debug("Starting the Server Timer Thread")
        handle_server_timer(self.server_connections_info, self.epoll, self.idle_time_out)


def handle_server_socket_events(epoll, server_socket, server_connections_info, server_requests, server_responses):
    """
        Description: Handles all the events happens in server side sockets
        
        input_param: epoll - Epoll listener bucket for the server socket
        input_type: epoll
        input_param: server_socket - Server listening socket
        input_type: socket
        
        out_param:
        out_type:
        
        sample output: None
    """
    try:
        while True:
            events = epoll.poll(TOT_CLIENT)
            for fileno, event in events:
                if fileno == server_socket.fileno():
                    connection, address = server_socket.accept()
                    connection.setblocking(0)
                    register_socket_epoll_event(epoll, connection.fileno(), select.EPOLLIN)
                    server_connections_info[connection.fileno()] = {'socket':connection, 'last_accessed_time': datetime.datetime.now()}
                    server_requests[connection.fileno()] = intialize_server_request_info()
                    server_responses[connection.fileno()] = intialize_server_response_info()
                elif event & select.EPOLLIN:
                    new_data = None
                    read_err = None
                    conn_info = server_connections_info[fileno]
                    conn_info['last_accessed_time'] = datetime.datetime.now()
                    req_info =  server_requests[fileno]
                    if req_info['req_start'] or req_info['rem_bytes_to_read']:
                        new_data = read_data(conn_info['socket'])
                        if not new_data:
                            logger.error("Read Failed so closing the connection from server\n")
                            read_err = True
                            modify_socket_epoll_event(epoll, fileno, 0)
                            shut_down_socket(conn_info['socket'])
                        if new_data and not req_info.get('full_header_received'):
                            req_info['req_start'] = False
                            req_info['header_data'] = req_info['header_data'] + new_data
                            if req_info['header_data'].find(EOL1) != -1 or req_info['header_data'].find(EOL2) != -1:
                                server_requests[fileno] = handle_client_request_data(server_requests[fileno])
                                req_info =  server_requests[fileno]
                                req_info['full_header_received'] = True
                        elif new_data and req_info['full_header_received'] and not req_info['is_chunked']:
                            req_info['received_bytes'] = req_info['received_bytes'] + len(new_data)
                            req_info['rem_bytes_to_read'] = req_info['rem_bytes_to_read'] - len(new_data)
                            req_info['data'] = req_info['data'] + new_data
                    if not req_info['rem_bytes_to_read'] and not read_err:
                        modify_socket_epoll_event(epoll, fileno, select.EPOLLOUT)
                        logger.info( '-'*40 + '\n' + req_info['header_data'])
                        logger.info(req_info['data'])
                        verify_client_request(req_info)
                        server_responses[connection.fileno()] = intialize_server_response_info(get_response(request_uri=req_info['uri']))
                elif event & select.EPOLLOUT:
                    conn_info = server_connections_info[fileno]
                    resp_info = server_responses[fileno]
                    conn_info['last_accessed_time'] = datetime.datetime.now()
                    if resp_info.get('rem_bytes_to_send'):
                        tot_sent = resp_info['sent_bytes']
                        resp_info['sent_bytes'] = tot_sent + send_data(conn_info['socket'], resp_info['response_data'][tot_sent:])
                        resp_info['rem_bytes_to_send'] = resp_info['tot_bytes_to_send'] - resp_info['sent_bytes']
                    else:
                        if resp_info.get('not_persistent'):
                            logger.debug("Not Persistent from server side\n")
                            modify_socket_epoll_event(epoll, fileno, 0)
                            shut_down_socket(conn_info['socket'])
                        else:
                            modify_socket_epoll_event(epoll, fileno, select.EPOLLIN)
                            server_requests[fileno] = intialize_server_request_info()
                            server_responses[fileno] = intialize_server_response_info()
                elif event & select.EPOLLHUP:
                    close_socket(epoll, fileno, server_connections_info)
                    del server_requests[fileno]
                    del server_responses[fileno]
    finally:
        epoll.unregister(server_socket.fileno())
        epoll.close()
        server_socket.close()

def start_http_server():
    """
        Description: Server HTTP Test start function
        
        input_param:
        input_type:
        
        out_param:
        out_type:
        
        sample output: 
    """

    server_connections_info = {}
    server_requests = {}
    server_responses = {}
    
    epoll = create_epoll()
    server_socket = creat_socket()
    logger.debug("Starting Server in port 8081")
    server_socket.bind(('0.0.0.0', 8081))
    server_socket.listen(TOT_CLIENT)
    register_socket_epoll_event(epoll,server_socket.fileno(), select.EPOLLIN)
    http_server_timer = HTTPServerTimer(server_connections_info, epoll, idle_time_out=60)
    http_server_timer.start()
    
    handle_server_socket_events(epoll, server_socket, server_connections_info, server_requests, server_responses)
    http_server_timer.join()
