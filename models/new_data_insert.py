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


def new_request_insert(http_details, update=None):
    """
        Description: Inserts the new record in the Request/Response
                     RequestVerification/ResponseVerification tables
        
        input_param: http_details - list of dictionary contains information
                                    for the new request details
        input_type: list
        
    """
    new_request = None
    for details in http_details:
         request = details.get('request')
         request_details = details.get('request_details')
         response_verifications = details.get('response_verification')
     
         response = details.get('response')
         response_details = details.get('response_details')
         request_verifications = details.get('request_verification')
     
         if request:
             if not update:
                 new_request = HttpRequest(**request)
                 session.add(new_request)
                 session.flush()
                 new_response = HttpResponse(request_id=new_request.id, **response)
                 session.add(new_response)
                 session.flush()
             else:
                  new_request = session.query(HttpRequest).get(request['id'])
                  new_request.is_active = True
                  new_request.pipe_line = False
                  new_request.category_id = request['category_id']
                  new_request.description = request['description']
                  new_request.total_request = request['total_requests']
                  new_response = session.query(HttpResponse).get(response['id'])
                  new_response.pipe_line = False
                  new_response.description = response['description']
                  new_response.total_response = response['total_response']
                  new_response.is_active = True
                  session.commit()
     
             if request_details:
                 all_requests = [ HttpSubRequest(request_id=new_request.id, 
                                      **request_detail ) 
                                  for request_detail in request_details 
                                ]
                 session.add_all(all_requests)
                 session.flush()
                 
                 response_index = 0
                 all_responses = [
                         HttpSubResponse(request_id=new_request.id, 
                                     response_id=new_response.id,
                                     sub_request_id=request.id, 
                                     **response_details[response_index])
                         for response_index, request in enumerate(all_requests)
                            if request.reach_server and response_details[response_index]
                     ]
                 session.add_all(all_responses)
                 session.flush()
     
                 if response_verifications:
                     all_response_verification = [ HttpResponseVerification(
                                                    request_id=new_request.id,
                                                    sub_request_id=all_requests[index].id,
                                                     **response_verification)
                      for index, response_verification in enumerate(response_verifications)
                        if response_verification
                     ]
                     session.add_all(all_response_verification)
                     session.flush()
                
                 if request_verifications:
                     all_request_verification = []
                     index = 0
                     for request_verification in request_verifications:
                         if request_verification and all_requests[index].reach_server:
                             all_request_verification.append(HttpRequestVerification(
                                                   request_id=new_request.id, 
                                                   sub_request_id=all_responses[index].sub_request_id,
                                                   sub_response_id=all_responses[index].id,
                                                   **request_verification)
                             )
                             index = index + 1
                     session.add_all(all_request_verification)
                     session.flush()
    return new_request.id if new_request else ''
