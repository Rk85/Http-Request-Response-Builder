from flask import Module
from flask import (
    render_template, 
    make_response, 
    request, 
    jsonify
)
import json
import logging
from db_tables.db_base import session
from db_tables.http_request import (
    HttpRequestCategory, 
    HttpRequestMethods, 
    HttpRequestHeaders,
    HttpData
)
from db_tables.http_response import (
    HttpResponseCodes, 
    HttpResponseHeaders
)

static_data_routes = Module(__name__, url_prefix="/static", name="static_data_routes")

# Mapper for the static data
static_data_mapper ={
    '1' :{
        'name' : 'Response Codes',
        'data' : lambda: [
                   {
                    'id': row.id,
                    'name': row.code_name,
                    'is_active': row.is_active
                   } for row in session.query(
                          HttpResponseCodes.id,
                          HttpResponseCodes.code_name,
                          HttpResponseCodes.is_active
                     ).all()
                 ],
        'column_names' : ['Id', 'Code Name', 'Active'],
        'form' : 'static_single_value.html',
        'post_url': '/static/codes/update'
    },
    '2' :{
        'name' : 'Request Methods',
        'data' : lambda: [
                   {
                    'id': row.id,
                    'name': row.method_name,
                    'is_active': row.is_active
                   } for row in session.query(
                          HttpRequestMethods.id,
                          HttpRequestMethods.method_name,
                          HttpRequestMethods.is_active
                     ).all()
                 ],
        'column_names' : ['Id', 'Method Name', 'Active'],
        'form' : 'static_single_value.html',
        'post_url': '/static/methods/update'
	},
    '3':{
        'name' : 'Request Categories',
        'data' : lambda: [
                   {
                    'id': row.id,
                    'name': row.category_name,
                    'is_active': row.is_active
                   } for row in session.query(
                          HttpRequestCategory.id,
                          HttpRequestCategory.category_name,
                          HttpRequestCategory.is_active
                     ).all()
                 ],
        'column_names' : ['Id', 'Code Name', 'Active'],
        'form' : 'static_single_value.html',
        'post_url': '/static/categories/update'
    },
    '4':{
        'name' : 'Request Headers',
        'data' : lambda: [
                   {
                    'id': row.id,
                    'header_name': row.header_name,
                    'sender_value': row.client_value,
                    'proxy_value': row.proxy_value,
                    'is_single_value': row.single_value_hdr,
                    'is_active': row.is_active
                   } for row in session.query(
                          HttpRequestHeaders.id,
                          HttpRequestHeaders.header_name,
                          HttpRequestHeaders.client_value,
                          HttpRequestHeaders.proxy_value,
                          HttpRequestHeaders.single_value_hdr,
                          HttpRequestHeaders.is_active,
                     ).all()
                 ],
        'column_names' : ['Id', 
                          'Header Name', 
                          'Client Value', 
                          'Proxy Value',
                           'Is Single Value',
                          'Active'],
        'form' : 'static_multi_value.html',
        'post_url': '/static/request_headers/update'
    },
    '5':{
        'name' : 'Response Headers',
        'data' : lambda: [
                   {
                    'id': row.id,
                    'header_name': row.header_name,
                    'sender_value': row.server_value,
                    'proxy_value': row.proxy_value,
                    'is_single_value': row.single_value_hdr,
                    'is_active': row.is_active
                   } for row in session.query(
                          HttpResponseHeaders.id,
                          HttpResponseHeaders.header_name,
                          HttpResponseHeaders.server_value,
                          HttpResponseHeaders.proxy_value,
                          HttpResponseHeaders.single_value_hdr,
                          HttpResponseHeaders.is_active,
                     ).all()
                 ],
        'column_names' : ['Id', 
                          'Header Name', 
                          'Server Value', 
                          'Proxy Value',
                           'Is Single Value',
                          'Active'],
        'form' : 'static_multi_value.html',
        'post_url': '/static/response_headers/update'
    }
}

update_details = {
            'categories' : {
                  'table_name' : HttpRequestCategory,
                  'attr_map': {'id': 'id',
                                'name': 'category_name',
                                'isActive': 'is_active'
                            }
             },
            'codes' : {
                  'table_name' : HttpResponseCodes,
                  'attr_map': {'id': 'id',
                                'name': 'code_name',
                                'isActive': 'is_active'
                            }
             },
            'methods' : {
                  'table_name' : HttpRequestMethods,
                  'attr_map': {'id': 'id',
                                'name': 'method_name',
                                'isActive': 'is_active'
                            }
             },
             'request_headers' : {
                  'table_name' : HttpRequestHeaders,
                  'attr_map': {'id': 'id',
                               'headerName': 'header_name',
                               'senderValue':'client_value',
                               'proxyValue': 'proxy_value',
                               'singleValueHeader':'single_value_hdr',
                               'isActive': 'is_active'
                            }
             },
             'response_headers' : {
                  'table_name' : HttpResponseHeaders,
                  'attr_map': {'id': 'id',
                               'headerName': 'header_name',
                               'senderValue':'server_value',
                               'proxyValue': 'proxy_value',
                               'singleValueHeader':'single_value_hdr',
                               'isActive': 'is_active'
                            }
             }
}

@static_data_routes.route('/types/<type_id>', methods=['GET'])
def get_static_type_details(type_id):
    """
        Description : View function to return the details
                      of a specfic static data
    """
    type_details = static_data_mapper.get(type_id)
    if type_details:
        response_data = {
                          'form' : render_template(type_details.get('form'), name=type_details.get('name', '')),
                          'data' : {
                                     'column_names' : type_details['column_names'],
                                     'post_url': type_details['post_url'],
                                     'row_data': type_details['data']()
                          }
                       }
        resp = make_response(jsonify(response_data), 200)
    else:
        resp = make_response(jsonify({}), 400)
    return resp
         
@static_data_routes.route('/types', methods=['GET'])
def get_static_types():
    """
        Description : View function to return the list of available
                      static data names
        
    """
    types = sorted([ 
              {
                'id': key,
                'name': value.get('name')
              }
              for key, value in static_data_mapper.iteritems() 
           ], key=lambda x: x['id'])
    response_data = { 'form' : render_template('static_data.html'),
                          'response_data' : {'types': types}
                     }
    resp = make_response(jsonify(response_data), 200)
    return resp

def update_change_item(items, mapper, attr_map):
    """
        Description : For given static data types, updates all the details
                      if present, and creates objects in the db it 
                      is not present
        input_param : items - details that need to updated to the static data
        input_type : list of dicts
        
        input_param : mapper name of the static table
        input_type : class
        
        input_param : attr_map - details the attribute map between form 
                       data and class attribute
        input_type : dict
 
    """
    edit_ids = [ item.get('id') for item in items ]
    db_objects = session.query(
                                 mapper
                               ).filter(
                                    mapper.id.in_(edit_ids)
                               ).all()
    for form_item in items: 
        if form_item.get('id') == 0:
            db_object = mapper()
            for key, attr_name in attr_map.iteritems():
                if attr_name != 'id':
                    setattr(db_object, attr_name, form_item.get(key))
                    session.add(db_object)
        else:
            for db_object in db_objects:
                if db_object.id == form_item.get('id'):
                    for key, attr_name in attr_map.iteritems():
                        setattr(db_object, attr_name, form_item.get(key))

@static_data_routes.route('/<types>/update', methods=['POST'])
def update_static_types(types):
    """
        Description : View function for specific static data Updation
        
    """
    form_data = request.json if request.json else request.form
    edited_items = form_data.get('edited')
    added_items = form_data.get('added')
    type_detail = update_details.get(types)
    if type_detail:
       update_change_item(edited_items, 
                          type_detail.get('table_name'),
                          type_detail.get('attr_map')
                         )
       session.commit()
       response_data = {
                      'post_response': {
                            'response_text': 'Data have beed saved successfully'
                       }
                    }
        
       resp = make_response(jsonify(response_data), 200)
    else:
        response_data = {'error': "unknown Static Data update"}
        resp = make_response(jsonify(response_data), 400)
    return resp
