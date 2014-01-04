from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys

Base = declarative_base()

dialect = 'mysql'
driver = ''
username = 'root'
password = 'hashini'
host = '127.0.0.1'
db_name = 'test'

if sys.version_info.major > 2:
    driver = '+pymysql'

create_query = dialect + driver + "://" + username + ":" + password + "@" + host + "/" + db_name

engine = create_engine(create_query)


#engine = create_engine('mysql+pymysql://root:hashini@127.0.0.1/test')
Session = sessionmaker(bind=engine)
session = Session()
db_connection = engine.connect()


# For the Table Creation
#import http_request
#import http_response
#import http_tests
#import http_verification
