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
Code common to both collection.py and granule.py
date: 2020-11-23
since: 0.0

A simple search interface for CMR. Use the search() function to perform searches.
This function can handle any query parameter which is supported by the CMR.

    search_by_page()
        base - CMR API end point directory
        query - a dictionary of CMR parameters
        filters - a list of filter lambdas
        page_state - a page_state dictionary for current page
        options - configurations

Queries can be modified to support sorting by using two base functions which
take in a query dictionary and modify it to include the sorting instructions.
    sort_by() : adds the sort key to the query
        sort_type - granule or collection
        params - original query
        *Sort (enum) - with values supported by CMR
    descending(): modify an existing sort key to be in reverse, or set it if provided
        sort_type - granule or collection
        params - original query
        Sort (enum) - Optional, with values supported by CMR

More information can be found at:
https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html

"""

#from enum import Enum, IntEnum
import sys

import cmr.util.common as common
import cmr.util.network as net
import cmr.util.logging as log

# ******************************************************************************
# utility functions

# ******************************************************************************
# filter function lambdas

def filter_none(item):
    """ Pass through, do no filtering - is this needed outside of testing?"""
    return item
def filter_meta(item):
    """return only the the meta objects"""
    if 'meta' in item:
        return item['meta']
    return item
def filter_umm(item):
    """return only the UMM part of the data"""
    if 'umm' in item:
        return item['umm']
    return item
def filter_concept_ids(item):
    """extract only fields that are used to identify a record"""
    if "meta" in item:
        meta = filter_meta(item)
        concept_id = meta['concept-id']
    elif "concept-id" in item:
        concept_id = item['concept-id']
    else:
        return item
    record = {'concept-id': concept_id}
    return record
def filter_drop(key):
    """drop a key from a dictionary"""
    return lambda dict : common.drop_key_safely(dict, key)

# ******************************************************************************
# internal functions

def _next_page_state(page_state, took):
    """Move page state object to the next page"""
    page_state['page_num'] = page_state['page_num'] + 1
    page_state['took'] = page_state['took'] + took
    return page_state

def _handle_all_filters(filter_list, item):
    """run through the list of filters and apply them"""
    result = item
    for filter_function in filter_list:
        result = filter_function(result)
    return result

def _handle_filters(filters, items):
    """handle filters or a single filter"""
    result = []

    if filters is None:
        result = items
    else:
        for item in items:
            if isinstance(filters, list):
                result.append(_handle_all_filters(filters, item))
            else:
                result.append(filters(item))
    return result

def _continue_download(hits, page_state):
    """
    Tests to see if enough items have been downloaded, as calculated after a
    download.
    Parameters:
        hits: total number of records from search
        page_state: position in the download ; current page
            * page_size: number of downloads per page
            * page_num: current page downloaded
            * limit: max records to download, -1 means all
    Returns:
        True if another page can be downloaded, False otherwise
    """
    items_downloaded = page_state['page_size']*page_state['page_num']
    limit = page_state['limit']
    # -1 means limit is never reached ; user requests that all records be downloaded
    under_limit = limit == -1 or items_downloaded < limit
    more_to_download = items_downloaded < hits
    return more_to_download and under_limit

def _standard_headers_from_options(options):
    """
    Create a dictionary with the CMR specific headers meant to be passed to urllib
    Parameters:
        options (dictionary): where to pull options from, responds to:
            * cmr-token: a CMR token, AKA an Echo Token, any token CMR will accept
            * X-Request-Id: Used for tracking requests across systems
            * Client-Id: Browser Agent Name
    Returns:
        dictionary with headers suitable for passing to urllib
    """
    headers = None
    headers = net.options_to_header(options, 'cmr-token', headers, 'Echo-Token')
    headers = net.options_to_header(options, 'X-Request-Id', headers)
    headers = net.options_to_header(options, 'Client-Id', headers, default='python_cmr_lib')
    return headers

def _cmr_url(base, query, page_state, options=None):
    """
    Create a GET url for calling CMR
    Parameters:
        base: CMR endpoint
        query: dictionary of search options
        page_state: current page information
        options: configurations, responds to:
            * env - sit, uat, or blank for production
    """
    expanded = net.expand_query_to_parameters(query)
    env = common.dict_or_default(options, 'env', '')
    if len(env)>0 and not env.endswith("."):
        env += "."
    url = ('https://cmr.{}earthdata.nasa.gov' +
        '/search/{}' +
        '?page_size={}' +
        '&page_num={}' +
        '&{}').format(env,
            base,
            page_state['page_size'],
            page_state['page_num'],
            expanded)
    return url

# ******************************************************************************
# public search functions

def sort_by(sort_type, params, sort):
    """
    Add sorting to the CMR parameters. This will change the params.
    Parameters:
        params(dictionary): the CMR parameters to add to
        sort(Sort): a value from the Sort enum
    Returns:
        params - can be chained
    """
    if params is not None and sort is not None and isinstance(sort, sort_type):
        params['sort_key'] = sort.value
    return params

def descending(sort_type, params, sort=None):
    """
    Add reverses the sorting in the CMR parameters. This will change the params.
    Parameters:
        params(dictionary): the CMR parameters to add to
        sort(Sort): Optional, will set the value from the Sort enum
    Returns:
        params - can be chained
    """
    if sort is not None:
        params = sort_by(sort_type, params, sort)
    if params is not None and 'sort_key' in params:
        value = params['sort_key']
        if not value.startswith('-'):
            params['sort_key'] = '-' + value
    return params

def create_page_state(page_size=100, page_num=1, took=0, limit=None):
    """Quick and dirty dictionary to hold page state for the recursive call"""
    if limit is None:
        limit = 20
    page_size = min(page_size, limit)
    return {'page_size': page_size, 'page_num': page_num, 'took':took, 'limit':limit}

def search_by_page(base, query=None, filters=None, page_state=None, options=None):
    """
    Recursive function to download all the pages of data. Note, this function
    will only run for 5 minutes and then will refuse to pull more pages
    returning what was found in that amount of time.
    Parameters:
        query (dictionary): CMR parameters and their values
        filters (list): A list of lambda functions to reduce the number of columns
        page_state (dictionary): the current page to download
        options (dictionary): configurations settings
    return collected items
    """
    if page_state is None:
        page_state = create_page_state()  # must be the first page

    headers = _standard_headers_from_options(options)
    accept = common.dict_or_default(options, 'accept',
        "application/vnd.nasa.cmr.umm_results+json")
    url = _cmr_url(base, query, page_state, options)
    log.logging.info(url)
    obj_json = net.get(url, accept=accept, headers=headers)
    if not isinstance(obj_json, str):
        resp_stats = {'hits': obj_json['hits'],
            'took': obj_json['took'],
            'items': obj_json['items']}

        resp_stats['items'] = _handle_filters(filters, resp_stats['items'])

        if _continue_download(resp_stats['hits'], page_state):
            next_page_state = _next_page_state(page_state, resp_stats['took'])
            max_time = common.dict_or_default(options, 'max_time', 300000)
            if next_page_state['took'] > max_time:
                # Do not allow searches to go on forever
                log.logging.warning("max search time exceeded")
                return resp_stats['items']
            recursive_items = search_by_page(base,
                query=query,
                filters=filters,
                page_state=next_page_state,
                options=options)
            resp_stats['items'] = resp_stats['items'] + recursive_items
    return resp_stats['items']

def open_api(section):
    """ Ask python to open up the API in a new browser window - unsupported!"""
    # Do not actually import this functionality if the user never asks for it.
    # This is a 'nice to have' function in Jupyter Notebook but is not a needed
    # function of the API, so some rule breaking is okay here.
    # Note, this function is not to be tested
    if 'webbrowser' not in sys.modules:
        # pylint: disable=C0415
        import webbrowser as web
    url = 'https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html'
    if section is not None:
        url = url + section
    web.open(url, new=2)

def print_help(prefix, functions, filters):
    """
    Built in help - prints out the public function names for the token API
    Parameters:
        filter(string): filters out functions beginning with this text, defaults to all
    """
    formater = common.help_format_lambda(prefix)

    out = __doc__
    out += ("\n**** Functions:\n")

    for item in functions:
        out += formater(item.__name__ + "()", item)

    out += "\n**** Filter Lambdas:\n"

    for item in filters:
        out += formater(item.__name__, item)

    return out
