from db_tables.db_base import session
from db_tables.http_response import HttpResponse, HttpSubResponse
from db_tables.http_request import HttpRequest, HttpSubRequest
from db_tables.http_tests import HttpTestResults, HttpServerTestFailureReason
import logging

logger = logging.getLogger()

def get_response(request_uri=None):
    """
        Description: Gets the next response data for the server
        
        input_param: request_uri - Request Uri present in client request
        input_type: string
        
        out_param: response_data - Response data as a string
        out_type: String
        
        sample output: "HTTP/1.1 200 OK\r\nConnection:Close\r\n\r\n"
        
    """

    
    if not request_uri:
        return {}
    test_id, req_id = [ int(parts) for parts in request_uri.strip().split("/")[:3] if len(parts) ]
    running_test_row = session.query(HttpTestResults)\
                    .filter(HttpTestResults.test_id==test_id)\
                    .filter(HttpTestResults.request_id==req_id)\
                    .filter(HttpTestResults.is_running==True).first()
    if running_test_row and running_test_row.sub_response_id:
        sub_response = session.query(HttpSubResponse).get(running_test_row.sub_response_id)
        if not sub_response:
            failure_data = "Proxy sent one extra request. The Request should have been served from cache"
            server_failure_reason = HttpServerTestFailureReason(reason=failure_data)
            session.add(server_failure_reason)
            session.flush()
            running_test_row.request_result=False
            running_test_row.server_failure_id = server_failure_reason.id
            session.commit()
            return "HTTP/1.1 404 Not Found\r\nConnection:Close\r\nContent-Length:0\r\n\r\n"
    else:
        failure_data = "Proxy sent one extra request. The Request should have been served from cache"
        server_failure_reason = HttpServerTestFailureReason(reason=failure_data)
        session.add(server_failure_reason)
        session.flush()
        running_test_row.request_result=False
        running_test_row.server_failure_id = server_failure_reason.id
        session.commit()
        return "HTTP/1.1 404 Not Found\r\nConnection:Close\r\nContent-Length:0\r\n\r\n"
    
    response_data = "HTTP/" + sub_response.version + " "
    response_data = response_data + sub_response.response_code.code_name + "\r\n"
    for response_header in sub_response.response_hdrs:
        response_data = response_data + response_header.header_name + ":"
        value_list = eval(response_header.server_value)
        if response_header.single_value_hdr:
            response_data = response_data + value_list[0]+ "\r\n"
        else:
            response_data = response_data + + ";".join(value_list) + "\r\n"
    if sub_response.data_id:
        response_data = response_data + "Content-Length:" + str( len(sub_response.data.data) )
        response_data = response_data + "\r\n\r\n"
        response_data = response_data + sub_response.data.data
    else:
        response_data = response_data + "Content-Length:0\r\n\r\n"
    logger.debug("Response From Server : " + response_data)
    return str(response_data)
