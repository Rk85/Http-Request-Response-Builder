from db_tables.http_request import HttpRequest, HttpSubRequest
from db_tables.http_response import HttpResponse, HttpSubResponse
from db_tables.http_tests import HttpTestResults, HttpTest
from db_tables.db_base import session, db_connection

def load_tests(name, 
                description,
                scheduled_by,
            category_id):
    """
        Description: Inserts the new record in the global Test Table
                        and copies the new tests requires into HttpTestResults
                        Table
        
        input_param: category_id - Test Type Id ( minor, major, critical)
        input_type: int
        
        out_param: test_id - Newly inserted test primary Id
        out_type: int
        
        sample output : 1
        
    """
    
    test_id = 0
    new_test = HttpTest(name=name, description=description, category_id=category_id, scheduled_by=scheduled_by)
    session.add(new_test)
    session.flush()
    session.commit()
    
    test_id = new_test.id
    
    requests = session.query(HttpRequest).filter(HttpRequest.category_id==category_id).all()
    for request in requests:
        sub_requests = session.query(HttpSubRequest).filter(HttpSubRequest.request_id==request.id).all()
        for sub_request in sub_requests:
            http_sub_response = session.query(HttpSubResponse).filter(HttpSubResponse.request_id==request.id).filter(HttpSubResponse.sub_request_id==sub_request.id).first()
            http_test = HttpTestResults(test_id=test_id,
                                request_id=request.id,
                                sub_request_id=sub_request.id,
                                response_id= http_sub_response.response_id if http_sub_response else None,
                                sub_response_id= http_sub_response.id if http_sub_response else None,
                                request_result=None,
                                response_result=None,
                                is_running=False,
                                is_completed=False,
                                server_failure_id=None,
                                client_failure_id=None,
                                no_of_times=1
                        )
                
            session.add(http_test)
    session.commit()
    return test_id
