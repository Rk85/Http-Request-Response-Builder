from db_tables.db_base import session
from db_tables.http_tests import HttpTestResults
from db_tables.http_request import HttpRequest, HttpSubRequest
from db_tables.http_response import HttpSubResponse
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy import not_

def get_next_request(test_id=0):
	"""
		description: Gets the next request data for the client
		
		param: test_id - Test Id of the client running test
		type: int
		
		rparam: request_data - Request data as a string
		rtype: String
		
		sample output: "GET /test HTTP/1.1\r\nConnection:Close\r\n\r\n"
		
	"""
	
	running_request_ids = [ test_result.request_id for test_result in session.query(HttpTestResults.request_id) \
							.filter(HttpTestResults.test_id==test_id)\
							.filter(HttpTestResults.is_running==True)\
							.filter(HttpTestResults.is_completed==False)\
							.order_by(HttpTestResults.request_id).all() ]
						
	next_request_query = session.query(HttpTestResults) \
						.filter(HttpTestResults.test_id==test_id)\
						.filter(HttpTestResults.is_running==False)\
						.filter(HttpTestResults.is_completed==False)
	if running_request_ids:
		next_request_query	= next_request_query.filter(not_(HttpTestResults.request_id.in_(running_request_ids)))
	next_request = next_request_query.order_by(HttpTestResults.request_id).first()
	if not next_request:
		print("All the requests are completed\n")
		return ''
	sub_request = session.query(HttpSubRequest)\
					.filter(\
							and_(HttpSubRequest.request_id==next_request.request_id, \
								HttpSubRequest.id==next_request.sub_request_id
							)
					).first()
	request_data = sub_request.method.method_name + " "
	request_data = request_data + "/" + str(test_id) + "/" + str(sub_request.request_id)
	request_data = request_data + " HTTP/" 
	request_data = request_data + sub_request.version + "\r\n"
	for request_header in sub_request.request_hdrs:
		request_data = request_data + request_header.header_name + ":" 
		value_list = eval(request_header.client_value)
		if request_header.single_value_hdr:
			request_data = request_data + value_list[0]+ "\r\n"
		else:
			request_data = request_data + ";".join(value_list) + "\r\n"
	if sub_request.data_id:
		request_data = request_data + "Content-Length:" + len(sub_request.data.data)
		request_data = request_data + "\r\n"
		request_data = request_data + sub_request.data.data
	else:
		request_data = request_data + "\r\n"
	
	next_request.is_running=True
	print("Setting  Test Running")
	session.commit()
	
	return str(request_data)

