"""
	Inserts the Staic Data in all the required static DB Tables
"""

import sys
import os
cwd = os.path.normpath(os.getcwd() + "/../")
sys.path.append(cwd)
from db_tables.db_base import session
from db_tables.http_response import ( HttpResponseCodes,
	HttpResponseHeaders,
	HttpResponse,
	HttpSubResponse
	)
from db_tables.http_request import ( HttpRequestMethods, 
	HttpRequestHeaders,
	HttpData,
	HttpRequestCategory,
	HttpRequest,
	HttpSubRequest,
	)
from db_tables.http_tests import ( HttpTest,
	HttpTestResults,
	HttpServerTestFailureReason,
	HttpClientTestFailureReason
	)
from db_tables.http_verification import ( HttpResponseVerification,
	HttpRequestVerification
	)
import hashlib

methods = [
			{'id' : 1, 'method_name' : 'OPTIONS', 'is_active': True },
			{'id' : 2, 'method_name' : 'HEAD', 'is_active': True },
			{'id' : 3, 'method_name' : 'GET', 'is_active': True },
			{'id' : 4, 'method_name' : 'POST', 'is_active': True },
			{'id' : 5, 'method_name' : 'DELETE', 'is_active': True }
		]

for method in methods:
	result = session.query(HttpRequestMethods).filter(HttpRequestMethods.id==method['id']).first()
	if not result:
		new_item = HttpRequestMethods(**method)
		session.add(new_item)

request_headers = [
					{'id': 1, 
						'header_name': 'Connection', 
						'client_value': "['Keep-Alive']", 
						'proxy_value': "['Keep-Alive', 'Close']",
						'single_value_hdr': True,
						'is_active' : True
					 }
				]
for request_header in request_headers:
	result = session.query(HttpRequestHeaders).filter(HttpRequestHeaders.id==request_header['id']).first()
	if not result:
		new_item = HttpRequestHeaders(**request_header)
		session.add(new_item)

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



http_data_details = [ 
						{ 'id': 1,
							'data': 'sample',
							'cksum': find_checksum(data='sample'),
							'is_active':True
						}
					]
for http_data in http_data_details:
	result = session.query(HttpData).filter(HttpData.id==http_data['id']).first()
	if not result:
		new_item = HttpData(**http_data)
		session.add(new_item)


categories = [
			{'id' : 1, 'category_name': 'testing', 'is_active': True}
		]

for category in categories:
	result = session.query(HttpRequestCategory).filter(HttpRequestCategory.id==category['id']).first()
	if not result:
		new_item = HttpRequestCategory(**category)
		session.add(new_item)


response_codes = [ 
			{'id' : 1, 'code_name' : '200 OK', 'is_active': True },
		]

for codes in response_codes:
	result = session.query(HttpResponseCodes).filter(HttpResponseCodes.id==codes['id']).first()
	if not result:
		new_item = HttpResponseCodes(**codes)
		session.add(new_item)

response_headers = [
					{'id': 1, 
						'header_name': 'Connection', 
						'server_value': "['Keep-Alive']", 
						'proxy_value': "['Keep-Alive', 'Close']",
						'single_value_hdr': True,
						'is_active' : True
					 }
				]
for response_header in response_headers:
	result = session.query(HttpResponseHeaders).filter(HttpResponseHeaders.id==response_header['id']).first()
	if not result:
		new_item = HttpResponseHeaders(**response_header)
		session.add(new_item)

session.commit()

http_details = [ { 
					'request':	{
								'is_active': True, 'category_id' : 1,
								'pipe_line' : False,'total_requests': 2,
								'description': 'Sample Test to verify Server Connection',
							},
					'request_details': [	{ 
											'method_id': 3,	'request_hdr_ids' : '1',
											'version' : 1.1, 'data_id' : None,
											'is_active': True, 'request_delay' : None,
											'reach_server': True
										},
										{
										'method_id': 3,	'request_hdr_ids' : '1',
										'version' : '1.1', 'data_id' : None,
										'is_active': True, 'request_delay' : None,
										'reach_server': False
									}],
					'response_verification' : [
											{ # These Verifications are done at client side
												'version': '1.1', 'response_code_id' : 1,
												'response_hdr_ids': '1', 'data_id':1
									},
									{ # These Verifications are done at client side
												 'version': '1.1', 'response_code_id' : 1,
												'response_hdr_ids': '1', 'data_id':1
									}
						],
					
					'response' : {'pipe_line' : False, 'description': 'Sample Test to verify Server Connection',
									'total_response': 1, 'is_active': True
								},
					'response_details' : [{	'version' : '1.1',
											'response_code_id': 1, 'response_hdr_ids': '1',
											'data_id': 1, 'is_active':True
									}],
					'request_verification': [
											{  # These Verification are done at server side
												'method_id': 3,
												'version':'1.1', 'request_hdr_ids':'1',
												'data_id': None
										}
						]
		}
]


for details in http_details:
	request = details.get('request')
	request_details = details.get('request_details')
	response_verifications = details.get('response_verification')
	
	response = details.get('response')
	response_details = details.get('response_details')
	request_verifications = details.get('request_verification')
	
	if request:
		new_request = HttpRequest(**request)
		session.add(new_request)
		session.flush()
		
		new_response = HttpResponse(request_id=new_request.id, **response)
		session.add(new_response)
		session.flush()
		
		if request_details:
			all_requests = [ HttpSubRequest(request_id=new_request.id, **request_detail ) for request_detail in request_details ]
			session.add_all(all_requests)
			session.flush()
			
			response_index = 0
			all_responses = []
			for request in all_requests:
				if request.reach_server:
					all_responses.append(HttpSubResponse(request_id=new_request.id, response_id=new_response.id,
											sub_request_id=request.id, **response_details[response_index]))
					response_index = response_index + 1
			session.add_all(all_responses)
			session.flush()
			
			if response_verifications:
				all_response_verification = [ HttpResponseVerification(request_id=new_request.id, sub_request_id=all_requests[index].id, 															 **response_verification)
												for index, response_verification in enumerate(response_verifications)]
				session.add_all(all_response_verification)
				session.flush()
			
			if request_verifications:
				all_request_verification = [ HttpRequestVerification(request_id=new_request.id, 
												sub_request_id=all_responses[index].sub_request_id, 															 								sub_response_id= all_responses[index].id, **request_verification)
												for index, request_verification in enumerate(request_verifications)]
				session.add_all(all_request_verification)
				session.flush()
				
session.commit()
