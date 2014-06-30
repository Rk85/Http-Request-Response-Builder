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
from tests import test_routes
from requests import request_routes
from shared import logger

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

@app.route('/')
def load_index():
    """
        Description : View function for the root URL
        
    """
    return render_template("index.html")                        

@app.route('/report/all_requests', methods=['GET'])
def report_all_requests():
    """
        Description : View function to render the configured request/response 
        
    """
    tests = [ format_test_data(test)    for test in session.query(HttpTest).all() ]
    response_data = { 'form' : render_template('all_requests.html'),
                          'response_data' : {'tests': tests}
                          }
    resp = make_response(jsonify(response_data), 200)
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

app.register_module(test_routes)
app.register_module(request_routes)

app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static_files':  os.path.join(os.getcwd(), 'static_files')
        })

app.jinja_loader = ChoiceLoader([MyTemplateLoader("templates")])

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
