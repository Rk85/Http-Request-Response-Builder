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
from db_tables.http_tests import HttpTest
from models.new_test_insert import load_tests

app = Flask(__name__)


class MyTemplateLoader(BaseLoader):

    def __init__(self, template_folder):
        self.template_folder = template_folder

    def get_source(self, environment, template_name):
        path = os.path.join(self.template_folder, template_name)
        if not os.path.exists(path):
            raise TemplateNotFound(template)
        fd = open(path, "r")
        source = "\r\n".join( fd.readlines() )
        return source, path, lambda : False
    

@app.route('/')
def load_index():
    return render_template("index.html")                        

@app.route('/schedule_new_test', methods=['GET', 'POST'])
def schedule_new_test():
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

@app.route('/report/all_test', methods=['GET', 'POST'])
def report_all_test():
	if request.method == 'GET':
		tests = []
		for test in session.query(HttpTest).all():
			test_info = {'id': test.id, 
					'name': test.name,
					'description': test.description,
					'created_time': test.created_time.isoformat(' '),
					'completed_time': test.completed_time.isoformat(' ')if test.completed_time else '',
					'scheduled_by' : test.scheduled_by,
					'category': test.test_category.category_name,
					'status' : "Running",
					'total_test_count' : len(test.total_tests)
				}
			pass_count = 0
			fail_count = 0
			status = "Pending"
			for sin_test in test.total_tests:
				if sin_test.request_result and sin_test.response_result:
					pass_count = pass_count + 1
				if test.running:
					status = "Running"
				elif test.completed:
					status = "Completed"
				elif test.paused:
					status = "Paused"
				else:
					status = "Pending"
				if not (sin_test.request_result or sin_test.response_result ) and ( status != "Pending" ):
					fail_count = fail_count + 1
				test_info.update ({ 'pass_count': pass_count,
								  'fail_count' : fail_count,
								  'status': status
							})
			tests.append(test_info)
		response_data = { 'form' : render_template('all_test_status.html'),
	                          'response_data' : {'tests': tests}
		                        }
		resp = make_response(jsonify(response_data), 200)
		return resp

@app.route('/new_tab/<page_id>')
def load_tab(page_id=0):
    resp = ''
    suites_available ={'suites': [ {'name': 'disk', 'id':1, 'selected':False}, {'name': 'disk1', 'id':2, 'selected':True}] }
    response_data = { 'form' : render_template('sample_with_controls - 1.html'),
                          'response_data' : suites_available
                        }
    resp = make_response(jsonify(response_data), 200)
    return resp

@app.route('/down_load_excel', methods=['GET', 'POST'])
def load_excel():
    if request.method == "POST":
           print request.form
    data = "<div>\
                <table>\
                <tr>\
                    <td>header</td>\
                </tr>\
                <tr>\
                    <td>Data</td>\
                </tr>\
                </table>\
            </div>"
    resp = make_response(data, 200)
    resp.headers['Content-Type'] = "text/plain"
    resp.headers['Content-Disposition'] = " attachment;filename=report.xls"
    return resp


app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static_files':  os.path.join(os.getcwd(), 'static_files')
        })

app.jinja_loader = ChoiceLoader([MyTemplateLoader("templates")])

if __name__ == '__main__':
    '''request = {'lob_name':'1', 'checklist':{'value':{'id':1,'name':'1'}, 'value':{'id':2, 'name':'2'}}}
    form_data = MultiDict(request)
    print form_data
    print form_data.get('checklist')
    print type(form_data.get('checklist'))'''
    app.run(debug=True, use_reloader=False)
