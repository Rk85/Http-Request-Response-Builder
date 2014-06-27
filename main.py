from tester_files.server.server import start_http_server
from tester_files.client.client import start_http_clients
from tester_files.server.server_timer import handle_server_timer
from db_tables.http_tests import HttpTest
from db_tables.db_base import session
import threading
import time
import logging
import os
from logging import config
ERROR_FORMAT = "%(levelname)s at %(asctime)s in function '%(funcName)s' in file \"%(pathname)s\" at line %(lineno)d: %(message)s"
DEBUG_FORMAT = "%(levelname)s at %(asctime)s in function '%(funcName)s' in file \"%(pathname)s\" at line %(lineno)d: %(message)s"
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
MAX_CONCURRENT_TESTS = 3


class HTTPClient(threading.Thread):
    """ 
        Description : HTTP Client Thread for Compliance Testing
        
    """
    def __init__(self, test_id):
        threading.Thread.__init__(self)
        self.test_id = test_id
    
    def run(self):
        """
            Description: Runs the Thread HTTP Client thread
            
            input_param:
            input_type:

            out_param:
            out_type:
            
            sample output:

        """
        logger.debug("Starting the clients Thread")
        start_http_clients(self.test_id)

class HTTPServer(threading.Thread):
    """
        Description : HTTP Server Thread for Compliance Testing
        
    """
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        """
            Description: Runs the Thread HTTP Server thread
            
            input_param:
            input_type:
            
            out_param:
            out_type:
            
            sample output:
        """
        logger.debug("Starting the server Thread")
        start_http_server()

if __name__ == "__main__":
    http_server = HTTPServer()

    http_server.start()
    time.sleep(2)
    while True:
        try:
            tot_running_tests = session.query(HttpTest).filter(HttpTest.running==True).count()
            if tot_running_tests < MAX_CONCURRENT_TESTS and not os.path.isfile("dont_run"):
                new_test = session.query(HttpTest).filter(HttpTest.running==False)\
                            .filter(HttpTest.completed==False).first()
                if new_test:
                    http_clients = HTTPClient(new_test.id)
                    http_clients.start()
                    new_test.running=True
                    #http_clients.join()
                    time.sleep(2)
            time.sleep(10)
        except Exception as e:
            logger.exception("Exception in Main thread " + str(e) )
    http_server.join()
