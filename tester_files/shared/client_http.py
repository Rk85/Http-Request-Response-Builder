from configs.client_config import EOL1, EOL2
from db_tables.db_base import session
from db_tables.http_response import HttpResponse, HttpSubResponse
from db_tables.http_verification import HttpResponseVerification
from db_tables.http_request import HttpRequest, HttpSubRequest
from db_tables.http_tests import HttpTestResults, HttpClientTestFailureReason
import hashlib

def find_checksum(data=None):
	"""
		description: Gets the MD5 hash of the given Data
		
		param: data - Data for which the MD5 Hash needs to be found
		type: int
		
		rparam: - Hash value of the given text
		rtype: String
		
		sample output: '14232342344234234'
		
	"""
	h = hashlib.md5()
	h.update(data.encode())
	return h.hexdigest()

def intialize_client_response_info():
	"""
		description: Initializes the client response dictionary
				with default values
		
		param: Response Received from the server
		type: string
		
		rparam: Returns the response details in a dictionary
		rtype: Dict
		
		sample output : {
				'full_header_received' : False,
				'headers' : {},
				'is_chunked' : False,
				'not_persistent' : False,
				'header_data' : 'Content-Length:13\r\nConnection:close\r\n'
				'status_line' : 'HTTP/1.1 200 OK'
				'data' : 'Hello World!',
				'received_bytes' : 0,
				'rem_bytes_to_read': 0,
				'tot_bytes_to_read': 0,
				'resp_start' : True
				}
	"""
	return {
			'full_header_received' : False,
			'full_header_received' : False,
			'headers' : {},
			'is_chunked' : False,
			'not_persistent' : True,
			'header_data' : '',
			'data' : '',
			'received_bytes' : 0,
			'rem_bytes_to_read': 0,
			'tot_bytes_to_read': 0,
			'resp_start' : True
			}


def intialize_client_request_info(request_data=None):
	"""
                description: Constructs the Request Details Dictionary 
				for the connection
		 
		param: header_data - Contains the plain request string
		type: string
		
		rparam: request header information stored in dict
		rtype: Dict
	
		sample Output: {
				'full_header_received' : False,
				'headers' : {},
				'is_chunked' : False,
				'not_persistent' : False,
				'header_length' : 10,
				'request_data' : 'GET /http HTTP/1.1\r\n
									HOST:http.com\r\nConnection:close\r\n\r\n
									Hello World!',
				'data_length' : 0
				'sent_bytes' : 0,
				'rem_bytes_to_send': 13,
				'tot_bytes_to_send': 13,
				'uri': '/http'
				}
	"""
	
	if request_data:
		data_start = find_data_start(request_data)
		request_data_length = len(request_data)
		if data_start == -1:
			data_start = request_data_length
		request_lines =  request_data[0:data_start].split("\r\n")
		uri = request_lines[0].split()[1]
		request_hdrs = dict([( \
					header_value.split(":")[0].strip().lower(), \
					header_value.split(":")[1].strip() \
					) for header_value in request_lines[1:] if header_value])
		return {
			'full_header_received' : data_start != request_data_length,
			'headers' : request_hdrs,
			'is_chunked' : request_hdrs.get('transfer-encoding'),
			'not_persistent' : request_hdrs.get('connection','keep-alive') == 'close',
			'header_length' : data_start,
			'data_length': data_start+3 if (data_start+3) != request_data_length else 0,
			'request_data' : request_data,
			'sent_bytes' : 0,
			'rem_bytes_to_send': len(request_data),
			'tot_bytes_to_send' : len(request_data),
			'uri': uri
        	}
	return {}

def find_data_start(data):
	"""
		description: Find the Start offset of HTTP Response Data
				in given data string
		
		param: data - All/Partial response data string received
		type:  string
		
		rparam: Response Data offset in the given string
		rtype: int
		
		sample output : 13
	"""
	if data.find(EOL1) != -1 :
		return data.find(EOL1)
	if data.find(EOL2) != -1:
		return data.find(EOL2)
	return -1

def handle_server_response_data(response=None):
	"""
		description: Handles the Response String/Headers at the client side
		
		param: Response Received from the server
		type: string
		
		rparam: Returns the response details in a dictionary
		rtype: Dict
		
		sample output : {
				'full_header_received' : True,
				'headers' : {},
				'is_chunked' : False,
				'not_persistent' : False,
				'header_data' : 'Connection:close\r\nContent-Length:13,
				'status_line' : 'HTTP/1.1 200 OK'
				'data' : 'Hello World!',
				'received_bytes' : 0,
				'rem_bytes_to_read': 0,
				'tot_bytes_to_read': 0
				}
	"""
	if response and response.get('header_data'):
		data_start = find_data_start(response.get('header_data'))
		if data_start != -1:
			response['data'] = response['header_data'][data_start+3:]
			response['header_data'] = response['header_data'][0:data_start]
		response_lines = response['header_data'].split("\r\n")
		response['status_line'] = response_lines[0] if response_lines else ''
		response_hdrs = dict([( \
					header_value.split(":")[0].strip().lower(), \
					header_value.split(":")[1].strip() \
					) for header_value in response_lines[1:] if header_value])
		response['full_header_received'] =  len(response['data']) > 0
		response['headers'] = response_hdrs
		response['is_chunked'] = response_hdrs.get('transfer-encoding')
		response['not_persistent'] = response_hdrs.get('connection') and response_hdrs.get('connection').lower() == 'close'
		response['tot_bytes_to_read'] = int(response_hdrs.get('content-length', 0))
		response['received_bytes'] = len(response['data'])
		response['rem_bytes_to_read'] = response['tot_bytes_to_read'] - response['received_bytes']
	return response

def verify_server_response(req_info, resp_info):
	"""
		description: Verifies the Server response for 
					1. Expected status line
					2. Response Header
					3. Data checksum if present
				and inserts the result in respective tables
	
		param: req_info - Request information Dictionary
		type:  dict
		
		param: resp_info - Response information Dictionary
		type:  dict
		
		sample output : None
	"""
	result = True
	result_reason = {'error':""}
	if req_info.get('uri'):
		test_id, req_id = [ int(parts) \
								for parts in req_info.get('uri').strip().split("/")[:3] \
								if len(parts) ]
		running_test_row = session.query(HttpTestResults)\
					.filter(HttpTestResults.test_id==test_id)\
					.filter(HttpTestResults.request_id==req_id)\
					.filter(HttpTestResults.is_running==True)\
					.filter(HttpTestResults.is_completed==False).first()
		if running_test_row:
			verification_details = session.query(HttpResponseVerification)\
									.filter(HttpResponseVerification.request_id==running_test_row.request_id)\
									.filter(HttpResponseVerification.sub_request_id==running_test_row.sub_request_id).first()
			if verification_details:
				status_line = "HTTP/" + verification_details.version + " " + verification_details.http_response_codes.code_name
				header_verification_result = verify_headers(verification_details.response_hdrs, resp_info, result_reason)
				if resp_info.get('status_line') == status_line and header_verification_result:
					if verification_details.data_id:
						if verification_details.http_data.cksum != find_checksum(resp_info['data']):  
							result=False
							result_reason['error'] = "CheckSum differes between expected and calculated from Response"
				else:
					if not result_reason['error']:
						result_reason['error'] = "Expected Status Line:" + status_line 
						result_reason['error'] = result_reason['error'] + " Does not Match with response: " + resp_info.get('status_line')
					result=False
			running_test_row.is_completed=True
			running_test_row.is_running=False
			if not result:
				client_failure_reason = HttpClientTestFailureReason(reason=result_reason['error'])
				session.add(client_failure_reason)
				session.flush()
				running_test_row.response_result=False
				running_test_row.client_failure_id = client_failure_reason.id
			else:
				running_test_row.response_result=True
			session.commit()

def set_test_completion(test_id, req_id):
	"""
		description: Before closing the socket, verify the closing socket requested
						completed successfuly or not
		
		param: test_id - Test Id of the given test
		type: int
		
		param: req_id - Request Id of the closing socket
		type:  int
		
		sample output : None
		
	"""
	running_test_row = session.query(HttpTestResults)\
                    .filter(HttpTestResults.test_id==test_id)\
                    .filter(HttpTestResults.request_id==req_id)\
                    .filter(HttpTestResults.is_running==True)\
                    .filter(HttpTestResults.is_completed==False).first()
	if running_test_row:
		reason = "Unexpected Event Happened in while receiving client response"
		client_failure_reason = HttpClientTestFailureReason(reason=reason)
		session.add(client_failure_reason)
		session.flush()
		running_test_row.response_result=False
		running_test_row.client_failure_id = client_failure_reason.id
		running_test_row.is_completed=True
		running_test_row.is_running=False
		session.commit()

def verify_headers(response_hdrs_list, resp_info, result_reason):
	"""
		description: Verifies the Response Header for correct value in them
		
		param: response_hdrs_list - Response header(HttpResponseHeaders) Table objects list
		type: list
		
		param: resp_info - Response information Dictionary
		type:  dict
		
		param: result_resason - Result of header verifications
		type:  dict
		
		sample output : True or False
		
	"""
	for header in response_hdrs_list:
		db_header_name = header.header_name.lower()
		response_headers = resp_info.get('headers')
		# If Verification is not present, exit the verification check
		if db_header_name not in response_headers.keys():
			result_reason['error'] = 'Header Name: ' + db_header_name + ' is not present in the response ' 
			result_reason['error'] = result_reason['error'] + response_headers
			return False
		value_list = eval(header.proxy_value)
		
		# If the header is single valued one
		# the value should be present in the db values list
		if header.single_value_hdr:
			if response_headers.get(db_header_name) not in value_list:
				result_reason['error'] = 'Single Value Header: ' + db_header_name + 'value: ' + value_list
				result_reason['error'] = result_reason['error'] + ' is not having the value from list: ' + response_headers.get(db_header_name)
				return False
		# If the Header is muti-valued one
		# All the values in li the list should be present in the header
		else:
			if set(value_list) - set(response_headers.get(db_header_name).split(";")):
				result_reason['error'] = 'Multi-Value Header: ' + db_header_name + 'value: ' + value_list
				result_reason['error'] = result_reason['error'] + ' is not having the all values from list: ' + response_headers.get(db_header_name)
				return False
	return True


