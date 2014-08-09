from flask import Module
from flask import (
    render_template, 
    make_response, 
    request, 
    jsonify
)
import json
import logging
from models.new_test_insert import load_tests
from models.new_data_insert import new_request_insert
from db_tables.http_tests import (
    HttpTest, 
    HttpTestResults
)
from db_tables.http_request import (
    HttpRequestCategory, 
    HttpRequest, 
    HttpSubRequest, 
    HttpRequestMethods, 
    HttpRequestHeaders
)
from db_tables.http_response import (
    HttpResponse, 
    HttpSubResponse, 
    HttpResponseCodes, 
    HttpResponseHeaders
)
from db_tables.http_verification import (
    HttpResponseVerification,
    HttpRequestVerification
)
from db_tables.db_base import session
from sqlalchemy.sql.expression import and_, or_
from shared import (
    logger, 
    format_main_details_data, 
    format_sub_request_data, 
    format_sub_response_data
)

request_routes = Module(__name__, url_prefix="/request", name="request_routes")

def format_request_details(form_data):
    """
        Description : Formats request data in the required format before
                      inserting them into the db
        
        input_param : form_data - Post data in a dictionary
        input_type : dict
        
        out_param : request_info_dict - formatted post data 
        out_type : dict
        
    """
    form_request = form_data.get('request', {})
    form_response = form_data.get('response', {})
    form_details = form_data.get('details', [])
    request_info_dict = {
          'request':{},
          'request_details':[],
          'response_verification':[],
          'response':{},
          'response_details':[],
          'request_verification':[]
    }
    request_info_dict['request'] = {
          'is_active': True,
          'pipe_line': False,
          'category_id': form_request.get('category_id'),
          'description': form_request.get('description'),
          'total_requests': len(form_data.get('details', [])),
    } 
    if form_request.get('id'):
        request_info_dict['request'].update({'id': form_request.get('id')})
    request_info_dict['response'] = {
          'is_active': True,
          'pipe_line': False,
          'description': form_response.get('description'),
          'total_response': 0,
    }
    if form_response.get('id'): 
        request_info_dict['response'].update({'id': form_response.get('id')})
    for detail in form_details:
        sub_request_details = detail.get('request_details')
        response_verification_details = detail.get('response_verification')
        request_info_dict['request_details'].append({
            'method_id': sub_request_details['method_id'],
            'request_hdr_ids': ','.join([str(id) for id in sub_request_details['request_hdr_ids']]),
            'version': sub_request_details['version'],
            'data_id': 1 if sub_request_details['data_id'].lower()=='yes' else None,
            'is_active':True,
            'request_delay': sub_request_details['request_delay'],
            'reach_server': sub_request_details['reach_server'].lower()=='yes'
        })
        request_info_dict['response_verification'].append({
            'version': response_verification_details['version'],
            'response_code_id': response_verification_details['response_code_id'],
            'response_hdr_ids': ','.join([str(id) for id in response_verification_details['response_hdr_ids']]),
            'data_id': 1 if response_verification_details['data_id'].lower()=='yes' else None
        })
        
        sub_response_details = detail.get('response_details')
        if sub_response_details:
            request_verification_details = detail.get('request_verification')
            request_info_dict['response']['total_response'] = request_info_dict['response']['total_response'] + 1
            request_info_dict['response_details'].append({
                'version': sub_response_details['version'],
                'response_code_id': sub_response_details['response_code_id'],
                'response_hdr_ids': ','.join([str(id) for id in sub_response_details['response_hdr_ids']]),
                'data_id': 1 if sub_response_details['data_id'].lower()=='yes' else None,
                'is_active': True
            })
            request_info_dict['request_verification'].append({
                'method_id': request_verification_details['method_id'],
                'version': request_verification_details['version'],
                'request_hdr_ids': ','.join([str(id) for id in request_verification_details['request_hdr_ids']]),
                'data_id': 1 if request_verification_details['data_id'].lower()=='yes' else None
            })
        else:
            request_info_dict['response_details'].append({})
            request_info_dict['request_verification'].append({})
    return request_info_dict


def get_static_datas():
    """
        Description : Gets details of the static tables
        
        out_param : formatted static table data
        out_type : dict
        
    """
    return {
         'categories' : [ 
                          {'id': category[0], 
                           'name': category[1] 
                          } for category in session.query(
                            HttpRequestCategory.id, 
                            HttpRequestCategory.category_name
                          ).all()
                        ],
         'methods' : [
                       {'id': method[0],
                           'name': method[1]
                          } for method in session.query(
                            HttpRequestMethods.id,
                            HttpRequestMethods.method_name
                         ).all()
											],
         'codes' : [
                       {'id': code[0],
                           'name': code[1]
                          } for code in session.query(
                            HttpResponseCodes.id,
                            HttpResponseCodes.code_name
                         ).all()
          ],
          'request_headers': [
                       { 'id': request_hdr.id,
                         'name': request_hdr.header_name,
                         'value': request_hdr.client_value
                       } for request_hdr in session.query(
                         HttpRequestHeaders.id,
                         HttpRequestHeaders.header_name,
                         HttpRequestHeaders.client_value
                        ).all()
          ],
          'request_verify_headers': [
                       { 'id': request_hdr.id,
                         'name': request_hdr.header_name,
                         'value': request_hdr.proxy_value
                       } for request_hdr in session.query(
                         HttpResponseHeaders.id,
                         HttpResponseHeaders.header_name,
                         HttpResponseHeaders.proxy_value
                        ).all()
          ],
          'response_headers': [
                       { 'id': response_hdr.id,
                         'name': response_hdr.header_name,
                         'value': response_hdr.server_value
                       } for response_hdr in session.query(
                         HttpResponseHeaders.id,
                         HttpResponseHeaders.header_name,
                         HttpResponseHeaders.server_value
                        ).all()
          ],
          'response_verify_headers': [
                       { 'id': response_hdr.id,
                         'name': response_hdr.header_name,
                         'value': response_hdr.proxy_value
                       } for response_hdr in session.query(
                         HttpRequestHeaders.id,
                         HttpRequestHeaders.header_name,
                         HttpRequestHeaders.proxy_value
                        ).all()
          ]
    }

@request_routes.route('/new', methods=['GET', 'POST'])
def new_request():
    """
        Description : View function for Request Configuration
        
    """
    if request.method == 'GET':
        response_data = {  
                             'form' : render_template('configure_request.html'),
                             'response_data' : get_static_datas()
                        }
        resp = make_response(jsonify(response_data), 200)
        return resp
    else:
        form_data = request.json if request.json else request.form
        if form_data.get('request') and form_data.get('response'):
            request_info_dict = format_request_details(form_data) 
            request_id = new_request_insert([request_info_dict])
            session.commit()
            response_text = """Your new request have beed saved with 
                                <b>Id : {0}""".format(request_id)
            response_data = { 
                      'post_response': { 
                            'response_text': response_text
                       }
                    }
            resp = make_response(jsonify(response_data), 200)
        else:
            response_data = {'error': "Unknown Data"}
            resp = make_response(jsonify(response_data), 400)
    return resp

@request_routes.route('/update/<int:request_id>', methods=['POST'])
def update_request(request_id):
    """
        Description : View function for Request Updation
        
    """
    form_data = request.json if request.json else request.form
    if form_data.get('request') and form_data.get('response'):
        # clean_previous_requests, to keep the logic simple
        # we delete all the details of this request group
        # and re-generate them using the details present in post request
        session.query(HttpSubResponse).filter(HttpSubResponse.request_id==request_id).delete()
        session.query(HttpSubRequest).filter(HttpSubRequest.request_id==request_id).delete()
        session.commit()
        request_info_dict = format_request_details(form_data) 
        new_request_insert([request_info_dict], True)
        session.commit()
        response_data = { 
                      'post_response': { 
                            'response_text': 'Data have beed saved successfully'
                       }
                    }
        resp = make_response(jsonify(response_data), 200)
    else:
        response_data = {'error': "unknown request"}
        resp = make_response(jsonify(response_data), 400)
    return resp


@request_routes.route('/details', methods=['GET'])
@request_routes.route('/details/<int:request_id>', methods=['GET'])
def load_all_requests(request_id=None):
    """
        Description : View function to render all the Request details
        
    """
    if not request_id:
        requests = [ format_main_details_data(request_details) 
                        for request_details in session.query(
                            HttpRequest).all() 
                   ]
        response_data = { 'form' : render_template('all_requests.html'),
                          'response_data' : {'requests': requests}
                          }
        resp = make_response(jsonify(response_data), 200)
        return resp
    else:
        show_request = session.query(HttpRequest).get(request_id)
        sub_request_query = session.query(HttpSubRequest
                               ).filter(HttpSubRequest.request_id==request_id)

        if request.method == 'GET':
            response_data = {  
                             'form' : render_template('request_details.html'),
                             'response_data' : {'request_details': {}}
                        }
            if show_request:
                response_data.update({  'form' : render_template('request_details.html'),
                                      'response_data' : {
                                            'main_details': format_main_details_data(show_request),
                                            'sub_request_details': [ format_sub_request_data(sub_request)
                                                for sub_request in sub_request_query ],
                                       }
                               })
            response_data.get('response_data', {}).update(get_static_datas())
            resp = make_response(jsonify(response_data), 200)
            return resp
