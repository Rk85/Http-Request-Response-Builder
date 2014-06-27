"""Mapper classes for the Http Tests

"""

from .db_base import Base, engine
from sqlalchemy import Column, Integer, String, DATETIME, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey, ForeignKeyConstraint
from .http_request import HttpRequest
from sqlalchemy.sql.expression import and_, func


class HttpTest(Base):
    """Contains Over-All Information of Each Test
    scheduled

    """
    __tablename__ = 'HttpTest'
    __table_args__ = {'useexisting' : True}
    
    id = Column("Id", Integer, primary_key=True)
    name = Column("TestName", String(1000), nullable=False)
    description = Column("TestDescription", String(1000), nullable=False)
    category_id = Column("CategoryId", Integer, ForeignKey("RequestCategory.Id"), nullable=False)
    paused = Column("TestPaused", Boolean, default=False, nullable=True)
    completed = Column("Completed", Boolean, default=False, nullable=True)
    running = Column("Running", Boolean, default=False, nullable=True)
    created_time = Column("CreatedDateTime", DATETIME, nullable=False, default=func.now())    
    completed_time = Column("CompletedTime", DATETIME, nullable=True)
    scheduled_by =  Column("ScheduledBy", String(1000), nullable=False)
    
    total_tests = relationship("HttpTestResults", backref="test_global_info")
    test_category = relationship("HttpRequestCategory", backref="test_global_info")

class HttpTestResults(Base):
    """For each scheduled test, we copy all the required informations
    from various tables into this Table. Each request/response is 
    handled to/from server and verified based on the information
    available from this table.
    
    """
    __tablename__ = 'HttpTestResults'
    __table_args__ = {'useexisting' : True}
    
    id = Column("Id", Integer, primary_key=True)
    test_id = Column("TestId", Integer, ForeignKey("HttpTest.Id"), nullable=False)
    
    request_id = Column("RequestId", Integer, ForeignKey("HttpRequest.Id"), nullable=False)
    sub_request_id = Column("SubRequestId", Integer, ForeignKey("HttpSubRequest.Id"), nullable=False)
    
    response_id = Column("ResponseId", Integer, ForeignKey("HttpResponse.Id"), nullable=True)
    sub_response_id = Column("SubResponseId", Integer, ForeignKey("HttpSubResponse.Id"), nullable=True)
    
    request_result = Column("ServerResult", Boolean)
    response_result = Column("ClientResult", Boolean)
    
    is_running = Column("TestRunning", Boolean)
    is_completed = Column("TestCompleted", Boolean)
    
    server_failure_id = Column("ServerTestFailureId", Integer, ForeignKey("HttpServerTestFailureReason.Id"), nullable=True)
    client_failure_id = Column("ClientTestFailureId", Integer, ForeignKey("HttpClientTestFailureReason.Id"), nullable=True)
    
    created_time = Column("CreatedDateTime", DATETIME, nullable=False, default=func.now())
    last_changed_time = Column("LastChangedTime", DATETIME, nullable=False, default=func.now())
    no_of_times = Column("NoOfTimes", Integer, nullable=True)
    
    http_request = relationship("HttpRequest", backref='http_tests')
    http_single_request = relationship("HttpSubRequest", backref='http_tests')
    http_single_response = relationship("HttpSubResponse", backref='http_tests')
    server_http_faliure = relationship("HttpServerTestFailureReason", backref='http_tests')
    client_http_faliure = relationship("HttpClientTestFailureReason", backref='http_tests')

class HttpServerTestFailureReason(Base):
    """For the Failed tests on the server side
    we store the reason    of failure in this Table

    """
    __tablename__ = 'HttpServerTestFailureReason'
    __table_args__ = {'useexisting' : True}
    
    id = Column("Id", Integer, primary_key=True)
    reason = Column("Reason", String(5000), nullable=False)

class HttpClientTestFailureReason(Base):
    """For the Failed tests on the client side
    we store the reason    of failure in this Table

    """
    __tablename__ = 'HttpClientTestFailureReason'
    __table_args__ = {'useexisting' : True}
    
    id = Column("Id", Integer, primary_key=True)
    reason = Column("Reason", String(5000), nullable=False)
