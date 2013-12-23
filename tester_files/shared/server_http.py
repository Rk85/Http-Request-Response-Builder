from configs.server_config import EOL1, EOL2
from db_tables.db_base import session
from db_tables.http_response import HttpResponse, HttpSubResponse
from db_tables.http_verification import HttpRequestVerification
from db_tables.http_request import HttpRequest, HttpSubRequest
from db_tables.http_tests import HttpTestResults, HttpServerTestFailureReason


def intialize_server_request_info():
	"""
		description: Intialize the server request dict with deffault values
		
		param: Request Data received by the server
		type: string
		
		rparam: Returns the request details in a dictionary
		rtype: Dict
		
		sample output : {
				'full_header_received' : False,
				'headers' : {},
				'is_chunked' : False,
				'not_persistent' : False,
				'header_data' : 'HOST:http.com\r\nConnection:close\r\n',
				'request_method': 'GET'
				'uri': '/http'
				'request_version' : ' HTTP/1.1'
				'data' : 'Hello World!',
				'received_bytes' : 0,
				'rem_bytes_to_read': 0,
				'tot_bytes_to_read': 0,
				'req_start' : True
				}
	"""
	
	return {
			'full_header_received' : False,
			'headers' : {},
			'is_chunked' : False,
			'not_persistent' : True,
			'header_data' : '',
			'request_method' : '',
			'uri' : '',
			'request_version' : '',
			'data' : '',
			'received_bytes' : 0,
			'rem_bytes_to_read': 0,
			'tot_bytes_to_read': 0,
			'req_start': True
		}
def intialize_server_response_info(response_data=None):
	"""
		description: Constructs the Response details to be sent
				to the client
		
		param: data - Contains the response string to be sent
					by server
		type: string
		
		rparam: request header information stored in dict
		rtype: Dict
	
		sample output : {
							'full_header_received' : False,
							'headers' : {},
							'is_chunked' : False,
							'not_persistent' : False,
							'header_length' : 10,	
							'response_data' : 'HTTP/1.1 200 OK\r\n
												Content Length: 100\r\nConnection:Close\r\n\r\n,
												Hello World!'
							'data_length' : 0
							'sent_bytes' : 0,
							'rem_bytes_to_send': 13,
							'tot_bytes_to_send': 13
					}
	"""
	if response_data:
		data_start = find_data_start(response_data)
		response_data_length = len(response_data)
		if data_start == -1:
			data_start = response_data_length
		response_lines = response_data[0:data_start].split("\r\n")
		response_hdrs = dict([( \
					header_value.split(":")[0].strip().lower(), \
					header_value.split(":")[1].strip() \
					) for header_value in response_lines[1:] if header_value ])
		return {
			 'full_header_received': data_start != response_data_length,
			 'headers' : response_hdrs,
			'is_chunked' : response_hdrs.get('transfer-encoding'),
			'not_persistent' : response_hdrs.get('connection', 'keep-alive').lower() == 'close',
			'header_length' : data_start,
			'data_length' : data_start+3 if (data_start+3) != response_data_length else 0,
			'response_data': response_data,
			'sent_bytes': 0,
			'rem_bytes_to_send': len(response_data),
			'tot_bytes_to_send' : len(response_data),
			}
	return {}

def find_data_start(data):
	"""
		description: Find the Start offset of HTTP Request Data
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

def handle_client_request_data(request=None):
	"""
		description: Handles the Request String/Headers at the server side
		
		param: Request Data received by the server
		type: string
		
		rparam: Returns the request details in a dictionary
		rtype: Dict
		
		sample output : {
				'full_header_received' : True,
				'headers' : {},
				'is_chunked' : False,
				'not_persistent' : False,
				'header_data' : 'HOST:http.com\r\nConnection:close\r\n',
				'request_method' : 'GET',
				'uri' :  '/test',
				'request_version' :  'HTTP/1.1',
				'data' : 'Hello World!',
				'received_bytes' : 0,
				'rem_bytes_to_read': 0,
				'tot_bytes_to_read': 0
				}
	"""
	if request and request.get('header_data'):
		data_start = find_data_start(request.get('header_data'))
		if data_start != -1:
			request['data'] = request['header_data'][data_start+3:]
			request['header_data'] = request['header_data'][0:data_start]
		request_hdrs = {}
		request_lines = request['header_data'].split("\r\n")
		if request_lines:
			request_line = request_lines[0].split()
			request['request_method'] = request_line[0]
			request['uri'] = request_line[1]
			request['request_version'] = request_line[2]
			
		request['request_line'] = request_lines[0] if request_lines else ''
		request_hdrs = dict([( \
					header_value.split(":")[0].strip().lower(), \
					header_value.split(":")[1].strip()
					) for header_value in request_lines[1:] if header_value ])	
		request['full_header_received'] =  len(request['header_data']) > 0
		request['headers'] = request_hdrs
		request['is_chunked'] = request_hdrs.get('transfer-encoding')
		request['not_persistent'] = request_hdrs.get('connection') and request_hdrs.get('connection').lower() == 'close'
		request['tot_bytes_to_read'] = int(request_hdrs.get('content-length', 0))
		request['received_bytes'] = len(request['data'])
		request['rem_bytes_to_read'] = request['tot_bytes_to_read'] - request['received_bytes']
	return request


def verify_client_request(req_info):
	"""
		description: Verifies the Client request for 
					1. Expected request line
					2. Request Header
					3. Data checksum if present
				and inserts the result in respective tables
	
		param: req_info - Request information Dictionary
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
			verification_details = session.query(HttpRequestVerification)\
									.filter(HttpRequestVerification.request_id==running_test_row.request_id)\
									.filter(HttpRequestVerification.sub_request_id==running_test_row.sub_request_id).first()
			if verification_details:
				request_line = verification_details.http_methods.method_name + " " 
				request_line = request_line + req_info.get('uri') + " HTTP/" + verification_details.version
				header_verification_result = verify_headers(verification_details.request_hdrs, req_info, result_reason)
				if req_info.get('request_line') == request_line and header_verification_result:
					if verification_details.data_id:
						if verification_details.http_data.cksum != find_checksum(req_info['data']):  
							result=False
							result_reason['error'] = "CheckSum differes between expected and calculated from Response"
				else:
					if not result_reason['error']:
						result_reason['error'] = "Expected Request Line:" + request_line 
						result_reason['error'] = result_reason['error'] + " Does not Match with request: " + req_info.get('request_line')
					result=False
			if not result:
				server_failure_reason = HttpServerTestFailureReason(reason=result_reason['error'])
				session.add(server_failure_reason)
				session.flush()
				running_test_row.request_result=False
				running_test_row.server_failure_id = server_failure_reason.id
			else:
				running_test_row.request_result=True
			session.commit()

def verify_headers(request_hdrs_list, req_info, result_reason):
	"""
		description: Verifies the Request Header for correct value in them
		
		param: request_hdrs_list - Request header(HttpRequestHeaders) Table objects list
		type: list
		
		param: req_info - Request information Dictionary
		type:  dict
		
		param: result_resason - Result of header verifications
		type:  dict
		
		sample output : True or False
		
	"""
	for header in request_hdrs_list:
		db_header_name = header.header_name.lower()
		request_headers = req_info.get('headers')
		# If Verification Header is not present, exit the verification check
		if db_header_name not in request_headers.keys():
			result_reason['error'] = 'Header Name: ' + db_header_name + ' is not present in the response ' 
			result_reason['error'] = result_reason['error'] + response_headers
			return False
		value_list = eval(header.proxy_value)
		
		# If the header is single valued one
		# the value should be present in the db values list
		if header.single_value_hdr:
			if request_headers.get(db_header_name) not in value_list:
				result_reason['error'] = 'Single Value Header: ' + db_header_name + 'value: ' + value_list
				result_reason['error'] = result_reason['error'] + ' is not having the value from list: ' + request_headers.get(db_header_name)
				return False
		# If the Header is muti-valued one
		# All the values in li the list should be present in the header
		else:
			if set(value_list) - set(request_headers.get(db_header_name).split(";")):
				result_reason['error'] = 'Multi-Value Header: ' + db_header_name + 'value: ' + value_list
				result_reason['error'] = result_reason['error'] + ' is not having the all values from list: ' + request_headers.get(db_header_name)
				return False
	return True


