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
        filters - a list of result filter lambdas
        page_state - a page_state dictionary for current page
        config - configurations

More information can be found at:
https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html

"""

import webbrowser as web
import cmr.util.common as common
import cmr.util.network as net
import cmr.util.logging as log

# ******************************************************************************
# filter function lambdas

def columns_pass(item):
    """ Pass through, do no filtering - is this needed outside of testing?"""
    return item
def columns_meta(item):
    """return only the the meta objects"""
    if 'meta' in item:
        return item['meta']
    return item
def columns_umm(item):
    """return only the UMM part of the data"""
    if 'umm' in item:
        return item['umm']
    return item
def columns_concept_ids(item):
    """extract only fields that are used to identify a record"""
    if "meta" in item:
        meta = item['meta']
        concept_id = meta['concept-id']
    elif "concept-id" in item:
        concept_id = item['concept-id']
    else:
        return item
    record = {'concept-id': concept_id}
    return record
def columns_drop(key):
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
    limit = page_state['limit'] # user requested limit
    items_downloaded = page_state['page_size']*page_state['page_num']
    more_to_download = items_downloaded < hits
    under_limit = items_downloaded < limit
    return more_to_download and under_limit

def _standard_headers_from_config(config):
    """
    Create a dictionary with the CMR specific headers meant to be passed to urllib
    Parameters:
        config (dictionary): where to pull configurations from, responds to:
            * cmr-token: a CMR token, AKA an Echo Token, any token CMR will accept
            * X-Request-Id: Used for tracking requests across systems
            * Client-Id: Browser Agent Name
    Returns:
        dictionary with headers suitable for passing to urllib
    """
    headers = None
    headers = net.config_to_header(config, 'cmr-token', headers, 'Echo-Token')
    headers = net.config_to_header(config, 'X-Request-Id', headers)
    headers = net.config_to_header(config, 'Client-Id', headers, default='python_cmr_lib')
    return headers

def _cmr_url(base, query, page_state, config=None):
    """
    Create a GET url for calling CMR
    Parameters:
        base: CMR endpoint
        query: dictionary of search options
        page_state: current page information
        config: configurations, responds to:
            * env - sit, uat, or blank for production
    """
    expanded = net.expand_query_to_parameters(query)
    env = common.dict_or_default(config, 'env', '').lower().strip()
    if len(env)>0 and not env.endswith("."):
        env += "."
    if env in ["prod", "ops"]:
        env = ""
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

def create_page_state(page_size=10, page_num=1, took=0, limit=10):
    """
    Quick and dirty dictionary to hold page state for the recursive call
    Parameters:
        page_size: number of hits per request, can be 1-2000, default to 10
        page_num: current page, can be 1-50, default to 1
        took: positive number, seconds of total processing
        limit: max records to return, 1-100_000, default to 10
    """
    page_size = max(1, min(page_size, 2000))
    page_num = max(1, min(page_num, 50))        # 2,000 * 50 = 100,000
    took = max(0, took)
    if limit is None:
        limit = 10
    limit = max(1, min(limit, 100_000))

    if limit<2000:
        # page_size and limit are the same thing in this case
        page_size = limit
    else:
        page_size = 2000
    return {'page_size': page_size, 'page_num': page_num, 'took':took, 'limit':limit}

def search_by_page(base, query=None, filters=None, page_state=None, config=None):
    """
    Recursive function to download all the pages of data. Note, this function
    will only run for 5 minutes and then will refuse to pull more pages
    returning what was found in that amount of time.
    Parameters:
        query (dictionary): CMR parameters and their values
        filters (list): A list of lambda functions to reduce the number of columns
        page_state (dictionary): the current page to download
        config (dictionary): configurations settings responds to:
            * accept - the format for the return defaults to UMM-JSON
            * max-time - total processing time allowed for all calls
    return collected items
    """
    if page_state is None:
        page_state = create_page_state()  # must be the first page

    headers = _standard_headers_from_config(config)
    accept = common.dict_or_default(config, 'accept',
        "application/vnd.nasa.cmr.umm_results+json")
    #url = _cmr_url(base, query, page_state, config)
    url = _cmr_url(base, '', page_state, config)
    log.logging.info(url)
    #obj_json = net.get(url, accept=accept, headers=headers)
    obj_json = net.post(url, query, accept=accept, headers=headers)
    if not isinstance(obj_json, str):
        resp_stats = {'hits': obj_json['hits'],
            'took': obj_json['took'],
            'items': obj_json['items']}

        resp_stats['items'] = _handle_filters(filters, resp_stats['items'])

        if _continue_download(resp_stats['hits'], page_state):
            next_page_state = _next_page_state(page_state, resp_stats['took'])
            max_time = common.dict_or_default(config, 'max-time', 300000)
            if next_page_state['took'] > max_time:
                # Do not allow searches to go on forever
                log.logging.warning("max search time exceeded")
                return resp_stats['items']
            recursive_items = search_by_page(base,
                query=query,
                filters=filters,
                page_state=next_page_state,
                config=config)
            resp_stats['items'] = resp_stats['items'] + recursive_items
    return resp_stats['items']

def open_api(section):
    """ Ask python to open up the API in a new browser window - unsupported!"""
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
