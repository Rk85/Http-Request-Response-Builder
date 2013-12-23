from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine('mysql+pymysql://root:hashini@127.0.0.1/test')
Session = sessionmaker(bind=engine)
session = Session()
db_connection = engine.connect()


# For the Table Creation
#import http_request
#import http_response
#import http_tests
#import http_verification
