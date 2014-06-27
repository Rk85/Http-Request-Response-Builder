from flask import Flask,render_template, make_response, request, jsonify
from werkzeug.datastructures import MultiDict
from jinja2 import ChoiceLoader,BaseLoader
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.wrappers import Request
import os
import sys
cwd = os.path.normpath(os.getcwd() + "/../")
sys.path.append(cwd)
from db_tables.db_base import session
from db_tables.http_request import HttpRequestCategory
from db_tables.http_tests import HttpTest, HttpTestResults
from models.new_test_insert import load_tests
from sqlalchemy.sql.expression import and_, or_
from flask.json import JSONEncoder

app = Flask(__name__)


class MyTemplateLoader(BaseLoader):
    """
        Description : Customized class to the templates through jinja
       
    """

    def __init__(self, template_folder):
        """
            Description : Init function to initialize the template loader class

        """
        self.template_folder = template_folder

    def get_source(self, environment, template_name):
        """
            Description : Returns the template details to the jinja environment
            
            input_param : environment - details of the jinja enviroment
            input_type : dict
            
            input_param : template_name - Name of the template to be rendered
            input_type : string
            
            out_param : source - template source
            out_type : string
            
            out_param : path - path of the template folder
            out_type : string
            
            out_param : lambda - function to check whether the template 
                            should be read again not. False-changed, 
                            True-not changed
            out_type : function object
        
        """
        path = os.path.join(self.template_folder, template_name)
        if not os.path.exists(path):
            raise TemplateNotFound(template)
        fd = open(path, "r")
        source = "\r\n".join( fd.readlines() )
        return source, path, lambda : False

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

@app.route('/')
def load_index():
    """
        Description : View function for the root URL
        
    """
    return render_template("index.html")                        

@app.route('/schedule_new_test', methods=['GET', 'POST'])
def schedule_new_test():
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

@app.route('/test_details/<int:test_id>', methods=['GET', 'POST'])
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

@app.route('/testcase_details/<int:test_id>', methods=['GET'])
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


@app.route('/report/test_status', methods=['GET'])
def report_test_statust():
    """
        Description : View function to load all the test results 
        
    """
	tests = [ format_test_data(test)	for test in session.query(HttpTest).all() ]
	response_data = { 'form' : render_template('all_test_status.html'),
	                      'response_data' : {'tests': tests}
	                      }
	resp = make_response(jsonify(response_data), 200)
	return resp

@app.route('/search_test', methods=['GET', 'POST'])
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
		
@app.route('/down_load_excel', methods=['POST'])
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
				excel_data = excel_data + "<td>" + str(td_value) + "</td>"
			excel_data = excel_data + "</tr>"
		excel_data = excel_data + "</tbody></table>"
	excel_data = excel_data + "</div>"
		
	resp = make_response(excel_data, 200)
	resp.headers['Content-Type'] = "text/plain"
	resp.headers['Content-Disposition'] = " attachment;filename=report.xls"
	return resp

@app.route('/help', methods=['GET', 'POST'])
def help():
    """
        Description : View function to handle help Page
        
    """
	response_data = { 'form' : render_template('help.html'),
                          'response_data' : {}
	                        }
	resp = make_response(jsonify(response_data), 200)
	return resp



app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static_files':  os.path.join(os.getcwd(), 'static_files')
        })

app.jinja_loader = ChoiceLoader([MyTemplateLoader("templates")])

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
