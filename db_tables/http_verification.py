"""Mapper classes for the Http Response/Request Verification
    
"""

from .db_base import Base, engine, session
from sqlalchemy import Column, Integer, String, DATETIME, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey, ForeignKeyConstraint
from sqlalchemy.sql.expression import and_, func
from .http_request import HttpRequest, HttpRequestHeaders
from .http_response import HttpResponseHeaders

class HttpResponseVerification(Base):
    """
        Description : For each pf the Http Request, once we receive the response
                      at the client side we refer this table for the passing 
                      criteria in the response
    
    """
    __tablename__ = 'HttpResponseVerification'
    __table_args__ = {'useexisting' : True}
    
    id = Column("Id", Integer, primary_key=True)
    
    request_id = Column("RequestId", Integer, ForeignKey("HttpRequest.Id"), nullable=False)
    sub_request_id = Column("SubRequestId", Integer, ForeignKey("HttpSubRequest.Id"), nullable=False)
    
    response_code_id = Column("ResponseCodeId", Integer, ForeignKey("ResponseCodes.Id"), nullable=False)
    version = Column("Version", String(100), nullable=False)
    response_hdr_ids = Column("ResponseHeaderIds", String(100), nullable=True)
    data_id = Column("DataId", Integer, ForeignKey("HttpData.Id"), nullable=True)
    
    http_request = relationship("HttpRequest", backref='http_response_verification')
    http_single_request = relationship("HttpSubRequest", backref='http_response_verification')
    http_data = relationship("HttpData", backref='http_response_verification')
    http_response_codes = relationship("HttpResponseCodes", backref='http_response_verification')
    
    @property
    def response_hdrs(self):
        response_hdr_ids_list = self.response_hdr_ids.split()
        return session.query(HttpResponseHeaders).filter(HttpResponseHeaders.id.in_(response_hdr_ids_list)).all()


class HttpRequestVerification(Base):
    """
        Description : For each of the Http Response, once we receive the request
                      at server side we refer this table for the passing criteria 
                      in the request
    
    """
    __tablename__ = 'HttpRequestVerification'
    __table_args__ = {'useexisting' : True}
    
    id = Column("Id", Integer, primary_key=True)
    
    request_id = Column("RequestId", Integer, ForeignKey("HttpRequest.Id"), nullable=False)
    sub_request_id = Column("SubRequestId", Integer, ForeignKey("HttpSubRequest.Id"), nullable=False)
    
    sub_response_id = Column("SubResponseId", Integer, ForeignKey("HttpSubResponse.Id"), nullable=False)
    
    method_id = Column("ResponseCodeId", Integer, ForeignKey("RequestMethods.Id"), nullable=False)
    version = Column("Version", String(100), nullable=False)
    request_hdr_ids = Column("RequestHeaderIds", String(100), nullable=True)
    data_id = Column("DataId", Integer, ForeignKey("HttpData.Id"), nullable=True)
    
    http_request = relationship("HttpRequest", backref='http_request_verification')
    http_single_response = relationship("HttpSubResponse", backref='http_request_verification')
    http_data = relationship("HttpData", backref='http_request_verification')
    http_methods = relationship("HttpRequestMethods", backref='http_response_verification')
    
    @property
    def request_hdrs(self):
        request_hdr_ids_list = self.request_hdr_ids.split()
        return session.query(HttpRequestHeaders).filter(HttpRequestHeaders.id.in_(request_hdr_ids_list)).all()

Base.metadata.create_all(engine)
