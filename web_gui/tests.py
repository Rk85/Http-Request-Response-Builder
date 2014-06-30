from flask import Module
from flask import render_template, make_response, request, jsonify
import json
import logging
from models.new_test_insert import load_tests
from db_tables.http_tests import HttpTest, HttpTestResults
from db_tables.http_request import HttpRequestCategory
from db_tables.db_base import session
from shared import format_test_data, format_test_case_data, logger
from sqlalchemy.sql.expression import and_, or_

test_routes = Module(__name__, url_prefix="/test", name="test_routes")

@test_routes.route('/new', methods=['GET', 'POST'])
def new_test():
    """
        Description : View function for the scheduling new tests
        
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

@test_routes.route('/search', methods=['GET', 'POST'])
def search_test():
    """
        Description : View function to handle search URL
        
    """
    if request.method == 'GET':
        data ={'categories': [ {'id': category[0], 'name': category[1] } for category in session.query(HttpRequestCategory.id, HttpRequestCategory.category_name).all()]}
        response_data = { 'form' : render_template('search_test.html'),
                          'response_data' : data
                            }
        resp = make_response(jsonify(response_data), 200)
        return resp
    else:
        response_data = { 'form' : render_template('all_test_status.html'),
                            'post_response' : {'tests': get_search_data()}
            }
        resp = make_response(jsonify(response_data), 200)
        return resp

@test_routes.route('/details', methods=['GET'])
def load_all_tests():
    """
        Description : View function to render all the test details
        
    """
    tests = [ format_test_data(test)    for test in session.query(HttpTest).all() ]
    response_data = { 'form' : render_template('all_test_status.html'),
                          'response_data' : {'tests': tests}
                          }
    resp = make_response(jsonify(response_data), 200)
    return resp


@test_routes.route('/details/<int:test_id>', methods=['GET', 'POST'])
def load_test_details(test_id=0):
    """
        Description : View function for loading the specific test details
        
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

@test_routes.route('/details/case/<int:test_id>', methods=['GET'])
def load_testcase_details(test_id=0):
    """
        Description : View function for loading the specific test case details
        
    """
    test_result_type = request.args.get('test_result_type', True)
    query = session.query(HttpTestResults)
    if test_result_type:
        print test_result_type
        query = query.filter(and_(HttpTestResults.request_result==test_result_type, HttpTestResults.response_result==test_result_type))
    else:
        print test_result_type
        query = query.filter(or_(HttpTestResults.request_result==test_result_type, HttpTestResults.response_result==test_result_type))
    test_cases = [ format_test_case_data(testcase) for testcase in query.all() ]
    response_data = {  'form' : render_template('test_details.html'),
                        'response_data' : {'testcase_details': test_cases}
            }
    resp = make_response(jsonify(response_data), 200)
    return resp

@test_routes.route('/details/down-load', methods=['POST'])
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

def get_search_data():
    """
        Description : Constructs the SQL search query based on the
                      given form data
        
        input_param :
        input_type :
        
        out_param : tests - mached HttpTest rows
        out_type : HttpTest
       
    """
    tests = []
    form_data = request.json if request.json else request.form
    query = session.query(HttpTest)
    if form_data.get('test_name'):
        query = query.filter( HttpTest.name==form_data.get('test_name') )
    if form_data.get('user_name'):
        query = query.filter( HttpTest.scheduled_by==form_data.get('user_name') )
    if form_data.get('category_ids'):
        query = query.filter( HttpTest.category_id.in_(form_data.get('category_ids') ))

    for test in query.all():
        tests.append(format_test_data(test))
    return tests

