from flask import Module
from flask import render_template, make_response, request, jsonify
import json
import logging
from models.new_test_insert import load_tests
from db_tables.http_tests import HttpTest, HttpTestResults
from db_tables.http_request import HttpRequestCategory, HttpRequest
from db_tables.db_base import session
from shared import format_test_data, format_test_case_data
from sqlalchemy.sql.expression import and_, or_
from shared import logger, format_request_data

request_routes = Module(__name__, url_prefix="/request", name="request_routes")

@request_routes.route('/new', methods=['GET', 'POST'])
def new_request():
    """
        Description : View function for Request Configuration
        
    """
    if request.method == 'GET':
        data ={'categories': [ {'id': category[0], 'name': category[1] } for category in session.query(HttpRequestCategory.id, HttpRequestCategory.category_name).all()]}
        response_data = { 'form' : render_template('schedule_new_test.html'),
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

@request_routes.route('/details', methods=['GET'])
def load_all_requests():
    """
        Description : View function to render all the Request details
        
    """
    requests = [ format_request_data(request_details)    for request_details in session.query(HttpRequest).all() ]
    response_data = { 'form' : render_template('all_requests.html'),
                          'response_data' : {'requests': requests}
                          }
    resp = make_response(jsonify(response_data), 200)
    return resp


@request_routes.route('/details/<int:test_id>', methods=['GET', 'POST'])
def load_request_details(test_id=0):
    """
        Description : View function for loading the specific Request details
        
    """
    test = session.query(HttpTest).get(test_id)
    if request.method == 'GET':
        response_data = {  'form' : render_template('test_details.html'),
                              'response_data' : {'test_details': {}}
                        }
        if test:
            response_data['response_data']['test_details'] = format_test_data(test)
        resp = make_response(jsonify(response_data), 200)
        return resp
    else:
        form_data = request.json if request.json else request.form
        test.paused = form_data.get('pause')
        test.running = not form_data.get('pause')
        session.commit()
        response_data = { 'post_response': { 'test_details' : format_test_data(test) }}
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
