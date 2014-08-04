"""Mapper classes for the Http Response

"""

from .db_base import Base, engine, session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DATETIME, Boolean
from sqlalchemy.schema import ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func
from .http_request import HttpRequest, HttpSubRequest

class HttpResponseCodes(Base):
    """
        Description : Supported Http Response Codes
    
    """
    __tablename__ = 'ResponseCodes'
    __table_args__ = {'useexisting' : True}
    
    id = Column("Id", Integer, primary_key=True)
    code_name = Column("CodeName", String(100), nullable=False)
    is_active = Column("isActive", Boolean)

class HttpResponseHeaders(Base):
    """
        Description : Static Http Response headers
    
    """
    __tablename__ = 'ResponseHeaders'
    __table_args__ = {'useexisting': True }
    
    id = Column("Id", Integer, primary_key=True)
    header_name = Column("HeaderName", String(1024), nullable=False)
    server_value = Column("HeaderValue", String(1024), nullable=False)
    proxy_value = Column("ProxyValue", String(1024), nullable=False)
    single_value_hdr = Column("SingleValueHeader", Boolean)
    is_active = Column("isActive", Boolean)


class HttpResponse(Base):
    """
        Description : Contains information about the global response
                       information for the Reseponse Section
    
    """
    __tablename__ = 'HttpResponse'
    __table_args__ = {'useexisting' : True}    

    id = Column("Id", Integer, primary_key=True)
    request_id = Column("RequestId", Integer, ForeignKey("HttpRequest.Id"), nullable=False)
    pipe_line = Column("PipeLine", Boolean)
    description = Column("Description", String(2000))
    total_response = Column("TotalResponses", Integer,  nullable=False)
    is_active = Column("IsActive", Boolean)
    
    http_request = relationship("HttpRequest", backref='http_response')


class HttpSubResponse(Base):
    """
        Description : Contains information about each of the responses
    
    """
    __tablename__ = 'HttpSubResponse'
    __table_args__ = {'useexisting' : True}
    
    id = Column("Id", Integer, primary_key=True)
    request_id = Column("RequestId", Integer, ForeignKey("HttpRequest.Id"), nullable=False)
    sub_request_id = Column("SubRequestId", Integer,  ForeignKey("HttpSubRequest.Id", ondelete="CASCADE"), nullable=False)
    response_id = Column("ResponseId", Integer, ForeignKey("HttpResponse.Id"), nullable=False)
    version = Column("Version", String(10), nullable=False)
    response_code_id = Column("ResponseCodeId", Integer, ForeignKey("ResponseCodes.Id"), nullable=False)
    response_hdr_ids = Column("ResponseHeaderIds", String(16000))
    is_active = Column("IsActive", Boolean)
    data_id = Column("DataId", Integer, ForeignKey("HttpData.Id"), nullable=True)
    
    http_request = relationship("HttpRequest", backref='http_single_response')
    http_response = relationship("HttpResponse", backref='http_single_response')
    response_code = relationship("HttpResponseCodes", backref='http_single_reponse')
    http_sub_request = relationship("HttpSubRequest", backref='http_single_response', uselist=False)
    
    data = relationship("HttpData", backref="htt_sinlge_response")
    
    @property
    def response_hdrs(self):
        response_hdr_ids_list = self.response_hdr_ids.split()
        return session.query(HttpResponseHeaders).filter(HttpResponseHeaders.id.in_(response_hdr_ids_list)).all()
