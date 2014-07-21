from flask import Module
from flask import render_template, make_response, request, jsonify
import json
import logging
from models.new_test_insert import load_tests
from db_tables.http_tests import HttpTest, HttpTestResults
from db_tables.http_request import HttpRequestCategory, HttpRequest, HttpSubRequest, HttpRequestMethods, HttpRequestHeaders
from db_tables.http_response import HttpResponse, HttpSubResponse, HttpResponseCodes, HttpResponseHeaders
from db_tables.http_verification import HttpResponseVerification
from db_tables.db_base import session
from sqlalchemy.sql.expression import and_, or_
from shared import logger, format_main_details_data, format_sub_request_data, format_sub_response_data

request_routes = Module(__name__, url_prefix="/request", name="request_routes")

@request_routes.route('/new', methods=['GET', 'POST'])
def new_request():
    """
        Description : View function for Request Configuration
        
    """
    if request.method == 'GET':
        data ={'categories': [ {'id': category[0], 'name': category[1] } for category in session.query(HttpRequestCategory.id, HttpRequestCategory.category_name).all()]}
        response_data = { 'form' : render_template('configure_request.html'),
                              'response_data' : data
                                }
        resp = make_response(jsonify(response_data), 200)

        return resp
    else:
        form_data = request.json if request.json else request.form
        load_test_args = { 'name' : form_data.get('test_name'),
                            'description' : form_data.get('description'),
                            'scheduled_by' : form_data.get('user_name'),
                            'category_id' : form_data.get('category_id')
                        }
        test_id = load_tests(**load_test_args)
        response_text = """Your test has been added in the que with <b>Id : {0}.</b> <br>
                        Please refer the staus of the test in the 
                        status page with the test id""".format(test_id)
        response_data = { 'post_response': { 'test_id' : 1, 'response_text': response_text}}
        resp = make_response(jsonify(response_data), 200)
        return resp

@request_routes.route('/update/<int:request_id>', methods=['POST'])
def update_request():
    """
        Description : View function for Request Updation
        
    """
    form_data = request.json if request.json else request.form
    print form_data
    response_data = { 'post_response': { }}
    resp = make_response(jsonify(response_data), 200)
    return resp


@request_routes.route('/details', methods=['GET'])
@request_routes.route('/details/<int:request_id>', methods=['GET'])
def load_all_requests(request_id=None):
    """
        Description : View function to render all the Request details
        
    """
    if not request_id:
        requests = [ format_main_details_data(request_details) for request_details in session.query(HttpRequest).all() ]
        response_data = { 'form' : render_template('all_requests.html'),
                          'response_data' : {'requests': requests}
                          }
        resp = make_response(jsonify(response_data), 200)
        return resp
    else:
        show_request = session.query(HttpRequest).get(request_id)
        sub_request_query = session.query(HttpSubRequest).filter(HttpSubRequest.request_id==request_id)

        if request.method == 'GET':
            response_data = {  'form' : render_template('request_details.html'),
                              'response_data' : {'request_details': {}}
                        }
            if show_request:
                response_data = {  'form' : render_template('request_details.html'),
                                      'response_data' : {
                                            'main_details': format_main_details_data(show_request),
                                            'sub_request_details': [ format_sub_request_data(sub_request)
                                                for sub_request in sub_request_query ],
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
                               }
            resp = make_response(jsonify(response_data), 200)
            return resp

@request_routes.route('/details/down-load', methods=['POST'])
def load_excel():
    """
        Description : View function to handle the Excel export data
        
    """
    result = get_search_data()
    excel_data = "<div>"
    if result:
        total_colums = len(result[0].keys())
        excel_data = excel_data + "</table><thead>"
        for key in result[0].keys():
            excel_data = excel_data + "<th>" + key + "</th>"
        excel_data = excel_data + "</thead><tbody>"
        for item in result:
            excel_data = excel_data + "<tr>"
            for td_value in item.values():
                try:
                    excel_data = excel_data + "<td>" + str(td_value) + "</td>"
                except UnicodeEncodeError as e:
                    logger.exception("Unicode error in excel download " + str(e))
            excel_data = excel_data + "</tr>"
        excel_data = excel_data + "</tbody></table>"
    excel_data = excel_data + "</div>"

    resp = make_response(excel_data, 200)
    resp.headers['Content-Type'] = "text/plain"
    resp.headers['Content-Disposition'] = " attachment;filename=report.xls"
    return resp
