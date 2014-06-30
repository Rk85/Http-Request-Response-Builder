import logging
from logging import config

ERROR_FORMAT = "%(levelname)s at %(asctime)s in function '%(funcName)s' in file \"%(pathname)s\" at line %(lineno)d: %(message)s"
DEBUG_FORMAT = "%(levelname)s at %(asctime)s in function '%(funcName)s' in file \"%(pathname)s\" at line %(lineno)d: %(message)s"
LOG_CONFIG = {'version':1,
              'formatters':{'error':{'format':ERROR_FORMAT},
                            'debug':{'format':DEBUG_FORMAT}},
              'handlers':{'console':{'class':'logging.StreamHandler',
                                     'formatter':'debug',
                                     'level':logging.DEBUG}
                                  },
              'root':{'handlers':['console'], 'level':'DEBUG'}}
logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger(__name__)


def format_test_data(test):
    """
        Description : Formats test data in the required format before
                      sending to the UI
        
        input_param : test - instance of HttpTest class
        input_type : HttpTest
        
        out_param : test_info - formatted test data 
        out_type : dict
        
    """
    test_info = {'id': test.id,
            'name': test.name.decode('latin1'),
            'description': test.description.decode('latin1'),
            'created_time': test.created_time.isoformat(' '),
            'completed_time': test.completed_time.isoformat(' ')if test.completed_time else '',
            'scheduled_by' : test.scheduled_by.decode('latin1'),
            'category': test.test_category.category_name,
            'status' : "",
            'total_test_count' : len(test.total_tests),
            'pass_count': 0,
            'fail_count': 0
        }
    pass_count = 0
    fail_count = 0
    status = "Pending"
    for sin_test in test.total_tests:
        if sin_test.request_result and sin_test.response_result:
            pass_count = pass_count + 1
        if test.completed:
            status = "Completed"
        elif test.running:
            status = "Running"
        elif test.paused:
            status = "Paused"
        else:
            status = "Pending"
        if not (sin_test.request_result and sin_test.response_result ) and ( status != "Pending" ):
            fail_count = fail_count + 1
    test_info.update ({ 'pass_count': pass_count,
                      'fail_count' : fail_count,
                      'status': status
            })
    return test_info

def format_test_case_data(data):
    """
        Description : Formats test case results data in the required 
                      format before sending to the UI
        
        input_param : data - instance of HttpTest class
        input_type : HttpTestResults
        
        out_param : test_case_info - formatted test data 
        out_type : dict
        
    """
    test_case_info = {
        'id': data.id,
        'test_id': data.test_id,
        'request_id': data.request_id,
        'sub_request_id': data.sub_request_id,
        'response_id': data.response_id,
        'sub_response_id' : data.sub_response_id,
        'request_result': data.request_result,
        'response_result': data.response_result,
        'is_running': data.is_running,
        'is_completed': data.is_completed,
        'created_time': data.created_time.isoformat(' '),
        'last_changed_time': data.last_changed_time.isoformat(' '),
        'server_failure_reason': data.server_http_faliure.reason if data.server_http_faliure else None,
        'client_failure_reason': data.client_http_faliure.reason if data.client_http_faliure else None
    }
    return test_case_info

def format_request_data(request_details):
    """
    """
    return {
        'id': request_details.id,
        'description': request_details.description,
        'category_name': request_details.category.category_name,
        'is_pipi_line' : request_details.pipe_line,
        'total_requests' : request_details.total_requests
    }
