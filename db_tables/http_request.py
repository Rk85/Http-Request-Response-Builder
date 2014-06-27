"""Mapper classes for the Http Request

"""

from .db_base import Base, engine, session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DATETIME, Boolean
from sqlalchemy.schema import ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func


class HttpRequestMethods(Base):
    """
        Description : Class for the Supported Http Methods 
    
    """
    __tablename__ = 'RequestMethods'
    __table_args__ = {'useexisting' : True}
    
    id = Column("Id", Integer, primary_key=True)
    method_name = Column("MethodName", String(10), nullable=False)
    is_active = Column("isActive", Boolean)

class HttpRequestHeaders(Base):
    """
        Description : Static Http Request Header Class
    
    """
    __tablename__ = 'RequestHeaders'
    __table_args__ = {'useexisting': True }
    
    id = Column("Id", Integer, primary_key=True)
    header_name = Column("HeaderName", String(1024), nullable=False)
    client_value = Column("HeaderValue", String(1024), nullable=False)
    proxy_value = Column("ProxyValue", String(1024), nullable=False)
    single_value_hdr = Column("SingleValueHeader", Boolean)
    is_active = Column("isActive", Boolean)

class HttpData(Base):
    """
        Description : Http Data for the Http Request/Response
    
    """
    __tablename__ = 'HttpData'
    __table_args__ = {'useexisting': True }

    id = Column("Id", Integer, primary_key=True)
    data = Column("Data", String(1048576), nullable=False)
    cksum = Column("CheckSum", String(1024), nullable=False)
    is_active = Column("isActive", Boolean)

class HttpRequestCategory(Base):
    """
        Description : Category for the Requests
    
    """
    __tablename__ = 'RequestCategory'
    __table_args__ = {'useexisting' : True}
    
    id = Column("Id", Integer, primary_key=True)
    category_name = Column("Name", String(20))
    is_active = Column("isActive", Boolean)

class HttpRequest(Base):
    """
        Description : Http Request class specifis the 
                     no of sub requests and other details for the request
    
    """
    __tablename__ = 'HttpRequest'
    __table_args__ = {'useexisting' : True}

    id = Column("Id", Integer, primary_key=True)
    is_active = Column("IsActive", Boolean)
    category_id = Column("CategoryId", Integer,ForeignKey("RequestCategory.Id"),  nullable=True)
    pipe_line = Column("PipeLine", Boolean)
    total_requests = Column("TotalRequests", Integer)
    description = Column("Description", String(2000))
    
    category = relationship("HttpRequestCategory", backref="http_request")    
    requests = relationship("HttpSubRequest", primaryjoin="HttpRequest.id==HttpSubRequest.request_id", \
                            backref="http_request")

class HttpSubRequest(Base):
    """
        Description : Contains details about each of the Http requests
    
    """
    __tablename__ = 'HttpSubRequest'
    __table_args__ = {'useexisting' : True}
    
    id = Column("Id", Integer, primary_key=True)
    request_id = Column("RequestId", Integer, ForeignKey("HttpRequest.Id"), nullable=False)
    method_id = Column("MethodId", Integer, ForeignKey("RequestMethods.Id"), nullable=False)
    request_hdr_ids = Column("RequestHdrIds", String(100), nullable=True)
    version = Column("Version", String(10), nullable=True)
    data_id = Column("DataId", Integer, ForeignKey("HttpData.Id"), nullable=True)
    is_active = Column("IsActive", Boolean)
    reach_server = Column("ServerRequest", Boolean)
    request_delay = Column("RequestDelay", Integer, nullable=True)
    
    method = relationship("HttpRequestMethods", backref="htt_single_request")
    data = relationship("HttpData", backref="htt_sinlge_request")
    
    @property
    def request_hdrs(self):
        request_hdr_ids_list = self.request_hdr_ids.split()
        return session.query(HttpRequestHeaders).filter(HttpRequestHeaders.id.in_(request_hdr_ids_list)).all()
