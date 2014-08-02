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

def format_main_details_data(request):
    """
        Description : Formats the main details of request and response
        
        input_arg : request - Details of the request that need 
                      to be formatted
        input_type : request - HttpRequest
        
        
        out_param : main_info - formatted dictionary
        out_type : dict
    """
    main_info = {}
    response = request.http_response[0]
    if response:
       main_info.update({
          'total_responses' : response.total_response,
          'response_description': response.description,
          'response_pipe_line' : response.pipe_line,
          'response_id': response.id
       })
    main_info.update({
        'id': request.id,
        'request_description': request.description,
        'request_category_name': request.category.category_name,
        'request_category_id': request.category.id,
        'request_pipe_line' : request.pipe_line,
        'total_requests' : request.total_requests
    })
    return main_info

def format_sub_request_data(sub_request):
    """
        Description : Formats the given sub request details
        
        input_arg : sub_request - Details of the request that need 
                      to be formatted
        input_type : sub_request - HttpSubRequest
        
        out_param : sub_request_info - formatted dictionary
        out_type : dict
    """
    sub_request_info = {}
    if sub_request.http_response_verification:
        verification = sub_request.http_response_verification[0]
        sub_request_info.update({
                                 'verify_code' : verification.http_response_codes.id if verification.http_response_codes else '',
                                 'verify_version' : verification.version,
                                 'verify_data_checksum' : True if verification.http_data else False,
                                 'verify_single_header' : [ header.single_value_hdr for header in verification.response_hdrs],
                                 'selected_request_verify_ids' : verification.response_hdr_ids.split(","),
        })
    sub_request_info.update({
        'id': sub_request.id,
        'selected_method_id': sub_request.method.id if sub_request.method else '',
        'selected_request_client_ids' : sub_request.request_hdr_ids.split(","),
        'version': sub_request.version,
        'data_size': len(sub_request.data.data) if sub_request.data else 0,
        'server_request': sub_request.reach_server,
        'request_delay': sub_request.request_delay,
    })
    if sub_request.http_single_response:
        sub_request_info['sub_response_details'] = format_sub_response_data(sub_request.http_single_response[0])
    return sub_request_info

def format_sub_response_data(sub_response):
    """
        Description : Formats the given sub response details
        
        input_arg : sub_response - Details of the response that need 
                      to be formatted
        input_type : sub_response - HttpSubResponse
        
        out_param : sub_response_info - formatted dictionary
        out_type : dict
    """
    sub_response_info = {}
    print "RKTEST", sub_response.http_request_verification
    if sub_response.http_request_verification:
        verification = sub_response.http_request_verification[0]
        sub_response_info.update( {
                                 'verify_method_id' : verification.http_methods.id if verification.http_methods else '',
                                 'verify_version' : verification.version,
                                 'selected_response_verify_ids' : verification.request_hdr_ids.split(","),
                                 'verify_data_checksum' : True if verification.http_data else False,
                                 'verify_single_header' : [ header.single_value_hdr for header in verification.request_hdrs]
        })
    sub_response_info.update({
        'id': sub_response.id,
        'version': sub_response.version,
        'selected_response_code' : sub_response.response_code.id if sub_response.response_code else '',
        'selected_response_server_ids' : sub_response.response_hdr_ids.split(","),
        'data_size': len(sub_response.data.data) if sub_response.data else 0,
        'request_id' : sub_response.sub_request_id
    })
    return sub_response_info

