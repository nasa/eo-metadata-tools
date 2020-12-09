# NASA EO-Metadata-Tools Python interface for the Common Metadata Repository (CMR)
#
#     https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html
#
# Copyright (c) 2020 United States Government as represented by the Administrator
# of the National Aeronautics and Space Administration. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

"""
date 2020-11-05
since 0.0
"""

import json
import urllib.parse
import urllib.request

import cmr.util.common as common

def get_local_ip():
    """ rewrite this stub"""
    return '127.0.0.1'

def value_to_param(key, value):
    """
    Convert a key value pair into a URL parameter pair
    """
    value = common.enum_value(value)
    encoded_key = urllib.parse.quote(key)
    encoded_value = urllib.parse.quote(value)
    result = encoded_key + "=" + encoded_value
    return result

def expand_parameter_to_parameters(key, parameter):
    """
    Convert a list of values into a list of URL parameters
    """
    result = []
    if isinstance(parameter, list):
        for item in parameter:
            param = value_to_param(key, item)
            result.append(param)
    else:
        value = common.enum_value(parameter)
        encoded_key = urllib.parse.quote(key)
        encoded_value = urllib.parse.quote(value)
        result.append(encoded_key + "=" + encoded_value)
    return result

def expand_query_to_parameters(query=None):
    """ Convert a dictionary to URL parameters """
    params = []
    if query is None:
        return ""
    for key in query:
        value = query[key]
        params = params + expand_parameter_to_parameters(key, value)
    return "&".join(params)

def apply_headers(req, headers):
    """Apply a headers to a urllib request object """
    if headers is not None and req is not None:
        for key in headers:
            value = headers[key]
            if value is not None and len(value)>0:
                req.add_header(key, value)

def transform_results(results, keys_of_interest):
    """
    Take a list of results and convert them to a multi valued dictionary. The
    real world use case is to take values from a list of collections and pass
    them to a granule search.

    [{key1:value1},{key1:value2},...] -> {"key1": [value1,value2]} ->
        &key1=value1&key1=value2 ( via expand_query_to_parameters() )
    """
    params = {}
    for item in results:
        for key in keys_of_interest:
            if key in item:
                value = item[key]
                if key in params:
                    params[key].append(value)
                else:
                    params[key] = [value]
    return params

def config_to_header(config, source_key, headers, destination_key=None, default=None):
    """
    Copy a value in the config into a header dictionary for use by urllib
    """
    config = config if isinstance(config, dict) else {}
    if destination_key is None:
        destination_key = source_key
    value = config.get(source_key, default)
    if destination_key is not None and value is not None:
        if headers is None:
            headers = {}
        headers[destination_key] = value
    return headers

def get(url, accept=None, client_id=None, headers=None):
    """
    Make a basic HTTP call to CMR using the GET action
    Parameters:
        url (string): resource to get
        accept (string): encoding of the returned data, some form of json is expected
        client_id (string): name of the client making the (not python or curl)
        headers (dictionary): HTTP headers to apply
    """
    req = urllib.request.Request(url)
    apply_headers(req, {'Accept': accept, 'Client-Id': client_id})
    apply_headers(req, headers)
    try:
        resp = urllib.request.urlopen(req)
        raw_response = resp.read().decode('utf-8')
        obj_json = json.loads(raw_response)
        return obj_json
    except urllib.error.HTTPError as exception:
        return exception

def post(url, body, accept=None, client_id=None, headers=None):
    """
    Make a basic HTTP call to CMR using the POST action
    Parameters:
        url (string): resource to get
        body (dictionary): parameters to send
        accept (string): encoding of the returned data, some form of json is expected
        client_id (string): name of the client making the (not python or curl)
        headers (dictionary): HTTP headers to apply
    """
    # Do not use the standard url encoder `urllib.parse.urlencode(body)` for the
    # body/data because it can not handle repeating values as required by CMR.
    # For example: `{'version': ['2', '3']}` must become `version=2&version=3`
    # not `version=[2, 3]`
    data = expand_query_to_parameters(body)
    data = data.encode('utf-8')
    req = urllib.request.Request(url, data)
    apply_headers(req, {'Accept': accept, 'Client-Id': client_id})
    apply_headers(req, headers)
    try:
        resp = urllib.request.urlopen(req)
        raw_response = resp.read().decode('utf-8')
        obj_json = json.loads(raw_response)
        return obj_json
    except urllib.error.HTTPError as exception:
        return exception
