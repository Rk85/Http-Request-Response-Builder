from tester_files.server.server import start_http_server
from tester_files.client.client import start_http_clients
from tester_files.server.server_timer import handle_server_timer
import threading
import time
import logging
from logging import config
ERROR_FORMAT = "%(levelname)s at %(asctime)s in function '%(funcName)s' in file \"%(pathname)s\" at line %(lineno)d: %(message)s"
DEBUG_FORMAT = "%(levelname)s at %(asctime)s in function '%(funcName)s' in file \"%(pathname)s\" at line %(lineno)d: %(message)s"
#DEBUG_FORMAT = "%(lineno)d in %(filename)s at %(asctime)s: %(message)s"
LOG_CONFIG = {'version':1,
              'formatters':{'error':{'format':ERROR_FORMAT},
                            'debug':{'format':DEBUG_FORMAT}},
              'handlers':{'console':{'class':'logging.StreamHandler',
                                     'formatter':'debug',
                                     'level':logging.DEBUG},
                          'file':{'class':'logging.FileHandler',
                                  'filename':'http_test.log',
                                  'formatter':'error',
                                  'level':logging.ERROR}},
              'root':{'handlers':['console'], 'level':'DEBUG'}}
logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger(__name__)


class HTTPClient(threading.Thread):
	"""
		HTTP Client Thread for Compliance Testing
	"""
	def __init__(self):
		threading.Thread.__init__(self)
	
	def run(self):
		"""
			description: Runs the Thread HTTP Server thread
			
			param:
			type:

			rparam:
			rtype:
			
			sample output:

		"""
		logger.debug("Starting the clients Thread")
		start_http_clients()

class HTTPServer(threading.Thread):
	"""
		HTTP Server Thread for Compliance Testing
	"""
	def __init__(self):
		threading.Thread.__init__(self)
	
	def run(self):
		"""
			description: Runs the Thread HTTP Server thread
			
			param:
			type:
			
			rparam:
			rtype:
			
			sample output:
		"""
		logger.debug("Starting the server Thread")
		start_http_server()

if __name__ == "__main__":
	http_server = HTTPServer()
	http_clients = HTTPClient()

	http_server.start()
	time.sleep(2)
	http_clients.start()
	
	http_server.join()
	http_clients.join()
