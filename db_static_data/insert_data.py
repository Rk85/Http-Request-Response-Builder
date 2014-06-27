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
        Description: Gets the MD5 hash of the given Data
        
        input_param: data - Data for which the MD5 Hash needs to be found
        input_type: int
        
        out_paran: - Hash value of the given text
        out_type: String
        
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
            {'id' : 1, 'category_name': 'testing', 'is_active': True},
            {'id' : 2, 'category_name': 'MUST', 'is_active': True},
            {'id' : 3, 'category_name': 'SHOULD', 'is_active': True},
            {'id' : 4, 'category_name': 'OPTIONAL', 'is_active': True},
            {'id' : 5, 'category_name': 'ALL', 'is_active': True}
            
        ]

for category in categories:
    result = session.query(HttpRequestCategory).filter(HttpRequestCategory.id==category['id']).first()
    if not result:
        new_item = HttpRequestCategory(**category)
        session.add(new_item)


response_codes = [ 
            {'id' : 1, 'code_name' : '200 OK', 'is_active': True },
            {'id' : 2, 'code_name' : '100 Continue', 'is_active': True},
            {'id' : 3, 'code_name' : '101 Switching Protocols', 'is_active': True},
            {'id' : 4, 'code_name' : '201 Created', 'is_active': True},
            {'id' : 5, 'code_name' : '202 Accepted', 'is_active': True},
            {'id' : 6, 'code_name' : '203 Non-Authoritative Information', 'is_active': True},
            {'id' : 7, 'code_name' : '204 No Content', 'is_active': True},
            {'id' : 8, 'code_name' : '205 Reset Content', 'is_active': True},
            {'id' : 9, 'code_name' : '206 Partial Content', 'is_active': True},
            {'id' : 10, 'code_name' : '300 Multiple Choices', 'is_active': True},
            {'id' : 11, 'code_name' : '301 Moved Permanently', 'is_active': True},
            {'id' : 12, 'code_name' : '302 Found', 'is_active': True},
            {'id' : 13, 'code_name' : '303 See Other', 'is_active': True},
            {'id' : 14, 'code_name' : '304 Not Modified', 'is_active': True},
            {'id' : 15, 'code_name' : '305 Use Proxy', 'is_active': True},
            {'id' : 16, 'code_name' : '307 Temporary Redirect', 'is_active': True},
            {'id' : 17, 'code_name' : '400 Bad Request', 'is_active': True},
            {'id' : 18, 'code_name' : '401 Unauthorized', 'is_active': True},
            {'id' : 19, 'code_name' : '402 Payment Required', 'is_active': True},
            {'id' : 20, 'code_name' : '403 Forbidden', 'is_active': True},
            {'id' : 21, 'code_name' : '404 Not Found', 'is_active': True},
            {'id' : 22, 'code_name' : '405 Method Not Allowed', 'is_active': True},
            {'id' : 23, 'code_name' : '406 Not Acceptable', 'is_active': True},
            {'id' : 24, 'code_name' : '407 Proxy Authentication Required', 'is_active': True},
            {'id' : 25, 'code_name' : '408 Request Time-out', 'is_active': True},
            {'id' : 26, 'code_name' : '409 Conflict', 'is_active': True},
            {'id' : 27, 'code_name' : '410 Gone', 'is_active': True},
            {'id' : 28, 'code_name' : '411 Length Required', 'is_active': True},
            {'id' : 29, 'code_name' : '412 Precondition Failed', 'is_active': True},
            {'id' : 30, 'code_name' : '413 Request Entity Too Large', 'is_active': True},
            {'id' : 31, 'code_name' : '414 Request-URI Too Large', 'is_active': True},
            {'id' : 32, 'code_name' : '415 Unsupported Media Type', 'is_active': True},
            {'id' : 33, 'code_name' : '416 Requested range not satisfiable', 'is_active': True},
            {'id' : 34, 'code_name' : '417 Expectation Failed', 'is_active': True},
            {'id' : 35, 'code_name' : '500 Internal Server Error', 'is_active': True},
            {'id' : 36, 'code_name' : '501 Not Implemented', 'is_active': True},
            {'id' : 37, 'code_name' : '502 Bad Gateway', 'is_active': True},
            {'id' : 38, 'code_name' : '503 Service Unavailable', 'is_active': True},
            {'id' : 39, 'code_name' : '504 Gateway Time-out', 'is_active': True},
            {'id' : 40, 'code_name' : '505 HTTP Version not supported', 'is_active': True}
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
                    'request':    {
                                'is_active': True, 'category_id' : 1,
                                'pipe_line' : False,'total_requests': 2,
                                'description': 'Sample Test to verify Server Connection',
                            },
                    'request_details': [    { 
                                            'method_id': 3,    'request_hdr_ids' : '1',
                                            'version' : 1.1, 'data_id' : None,
                                            'is_active': True, 'request_delay' : None,
                                            'reach_server': True
                                        },
                                        {
                                        'method_id': 3,    'request_hdr_ids' : '1',
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
                    'response_details' : [{    'version' : '1.1',
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
                all_response_verification = [ HttpResponseVerification(request_id=new_request.id, sub_request_id=all_requests[index].id,                                                              **response_verification)
                                                for index, response_verification in enumerate(response_verifications)]
                session.add_all(all_response_verification)
                session.flush()
            
            if request_verifications:
                all_request_verification = [ HttpRequestVerification(request_id=new_request.id, 
                                                sub_request_id=all_responses[index].sub_request_id,                                                                                              sub_response_id= all_responses[index].id, **request_verification)
                                                for index, request_verification in enumerate(request_verifications)]
                session.add_all(all_request_verification)
                session.flush()
                
session.commit()
