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

import logging
import math
import webbrowser as web

import cmr.util.common as common
import cmr.util.network as net

# ******************************************************************************
# filter function lambdas

logging.basicConfig(level = logging.ERROR)
logger = logging.getLogger('cmr.search.common')

def all_fields(item):
    """
    Makes no change to the item, passes through. Used primarily as an example
    and for testing the filter workflow
    """
    return item
def meta_fields(item):
    """Return only the the meta objects"""
    if 'meta' in item:
        return item['meta']
    return item
def umm_fields(item):
    """Return only the UMM part of the data"""
    if 'umm' in item:
        return item['umm']
    return item
def concept_id_fields(item):
    """Extract only fields that are used to identify a record"""
    if "meta" in item:
        meta = item['meta']
        concept_id = meta['concept-id']
    elif "concept-id" in item:
        concept_id = item['concept-id']
    else:
        return item
    record = {'concept-id': concept_id}
    return record
def drop_fields(key):
    """Drop a key from a dictionary"""
    return lambda dict : common.drop_key_safely(dict, key)

# ******************************************************************************
# internal functions

def _next_page_state(page_state, took):
    """Move page state dictionary to the next page"""
    page_state['page_num'] = page_state['page_num'] + 1
    page_state['took'] = page_state['took'] + took
    return page_state

def _continue_download(page_state):
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
    return items_downloaded<limit

# document-it: {"key":"cmr-token", "default":"None", "msg":"also known as the echo token"}
# document-it: {"key":"X-Request-id", "default":"None"}
# document-it: {"key":"Client-Id", "default":"python_cmr_lib"}
# document-it: {"key":"User-Agent", "default":"python_cmr_lib"}
def _standard_headers_from_config(config: dict):
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
    headers = net.config_to_header(config, 'User-Agent', headers, default='python_cmr_lib')
    return headers

# document-it: {"from":"._cmr_basic_url"}
def _cmr_query_url(base: str, query: dict, page_state: dict, config: dict = None):
    """
    build a collection or granule search URL to CMR
    Parameters:
        base: CMR endpoint
        query: dictionary url parameters
        config: configurations, responds to:
            * env - sit, uat, ops, prod, production, or blank for production
    """
    if query is None:
        query = {}
    if int(page_state['limit'])>2000:
        query = common.conj(query, {'scroll': 'true'})
    query = common.conj(query, {'page_size': page_state['page_size']})
    return _cmr_basic_url(base, query, config)

# document-it: {"key":"env", "default":"", "msg":"uat, ops, prod, production, or blank for ops"}
def _cmr_basic_url(base: str, query: dict, config: dict = None):
    """
    Create a url for calling any CMR search end point, should not make any
    assumption, beyond the search directory. Will auto set the envirnment based
    on how config is set
    Parameters:
        base: CMR endpoint
        query: dictionary url parameters
        config: configurations, responds to:
            * env - sit, uat, ops, prod, production, or blank for production
    """
    expanded = ""
    if query is not None and len(query)>0:
        expanded = "?" + net.expand_query_to_parameters(query)

    config = common.always(config)
    env = config.get('env', '').lower().strip()
    if len(env)>0 and not env.endswith("."):
        env += "."
    if env in ['', 'ops', 'prod', 'production']:
        env = ""

    url = ('https://cmr.{}earthdata.nasa.gov/search/{}{}').format(env, base, expanded)
    return url

# document-it: {"key":"accept", "default":"application/vnd.nasa.cmr.umm_results+json"}
# document-it: {"from":"._standard_headers_from_config"}
# document-it: {"from":"._cmr_query_url"}
def _make_search_request(base: str, query: dict, page_state: dict, config: dict):
    """
    Do the first half of the "search_by_page" function, by making the call to CMR.
    Build a request and issue it, returning a json object
    Parameters:
        base (string): the CMR end point, the base of the URL before params
        query (dictionary): CMR parameters and their values
        page_state (dictionary): the current page to download
        config (dictionary): configurations settings responds to:
            * accept - the format for the return defaults to UMM-JSON
    Returns:
        JSON object with either data from CMR, or on error you get the error response
    """
    # Build headers
    headers = _standard_headers_from_config(config)
    if 'CMR-Scroll-Id' in page_state:
        logger.debug('Setting scroll id to %s.', page_state['CMR-Scroll-Id'])
        headers = common.conj(headers, {'CMR-Scroll-Id': page_state['CMR-Scroll-Id']})
    accept = config.get('accept', 'application/vnd.nasa.cmr.umm_results+json')
    headers = common.conj(headers, {'Accept': accept})

    # Build URL and make POST
    url = _cmr_query_url(base, None, page_state, config = config)
    logger.info(' - %s: %s', 'POST', url)
    obj_json = net.post(url, query, headers=headers)

    return obj_json

def _error_object(code, message):
    """
    Construct a dictionary containing all the fields an error should have
    Parameters:
        code(int): error code, >0 is HTML, <=0 are internal error codes
        message(string): error message
    Returns:
        Dictionary with errors, code, and reason keys
    """
    return {'errors': [message], 'code':code, 'reason': message}

# ******************************************************************************
# public search functions

def create_page_state(page_size = 10, page_num = 1, took = 0, limit = 10):
    """
    Dictionary to hold page state for the recursive call
    Parameters:
        page_size: number of hits per request, can be 1-2000, default to 10
        page_num: current page, can be 1-50, default to 1
        took: positive number, seconds of total processing
        limit: max records to return, 1-100000, default to 10
    """

    # Ensure bounds are followed
    page_size = max(1, min(page_size, 2000))
    page_num = max(1, min(page_num, 50))        # 2,000 * 50 = 100,000
    took = max(0, took)
    if limit is None:
        limit = 10
    limit = max(0, min(limit, 100000))

    # Setup Page Size based on limit
    if limit<=2000:
        # page_size and limit are the same thing in this case
        page_size = limit
    else:
        # Calculate the optimal page size to ensure that the code does not
        # download more records then need to be. Base example is requesting
        # 2048 records, but not wanting to download 2 pages of 2000 to get 4000
        # records. Instead 3 pages of 683 for a total of 2049 records, only 1
        # over instead of 1952 (4000-2048).

        if limit%2000 == 0:
            page_size = 2000
        else:
            optimal_page_count = math.ceil(limit/2000)+1
            page_size = math.ceil(limit/optimal_page_count)
            overage = (optimal_page_count * page_size) - limit
            logger.info("page size is %d and overage is %d.", page_size, overage)
    return {'page_size': page_size, 'page_num': page_num, 'took':took, 'limit':limit}


# document-it: {"from": "._standard_headers_from_config"}
# document-it: {"from":"._cmr_basic_url"}
def clear_scroll(scroll_id, config: dict = None):
    """
    This action is called to clear a scroll ID from CMR allowing CMR to free up
    memory associated with the current search.

    This call is the same as calling the following CURL command:
    curl -i -XPOST -H "Content-Type: application/json" \
        https://cmr.earthdata.nasa.gov/search/clear-scroll \
        -d '{ "scroll_id" : "xxxx"}'
    This API call must send " and not '
    API call returns HTTP status code 204 when successful.

    Parameters:
        scroll_id(string/number): CMR Scroll ID
        config(dictionary) - used to make configurations changes
    Returns:
        error dictionary if there was a problem, otherwise a JSON object of response headers
    """
    config = common.always(config)

    # Build headers
    headers = _standard_headers_from_config(config)
    headers = common.conj(headers, {'Content-Type': 'application/json'})

    url = _cmr_basic_url('clear-scroll', None, config)
    data = '{"scroll_id": "' + str(scroll_id) + '"}'
    logger.info(" - %s: %s", 'POST', url)
    obj_json = net.post(url, data, headers=headers)
    if 'errors' in obj_json:
        errors = obj_json['errors']
        for err in errors:
            logger.warning(" Error while clearing scroll: %s", err)
    return obj_json

def apply_filters(filters, items):
    """
    Apply all filters to the collection of data, returning the results
    Parameters:
        filters(list): list of or a single lambda function to apply to items
        items(list): list of objects to be processed
    Return:
        the results of the filters
    """
    result = []

    if filters is None:
        result = items
    else:
        for item in items:
            if isinstance(filters, list):
                filtered_item = item
                for filter_function in filters:
                    filtered_item = filter_function(filtered_item)
                result.append(filtered_item)
            else:
                result.append(filters(item))
    return result

# document-it: {"key":"max-time", "default": "300000"}
# document-it: {"from":"._make_search_request"}
def search_by_page(base, query = None, filters = None, page_state = None, config: dict = None):
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
    config = common.always(config)
    if page_state is None:
        page_state = create_page_state()  # must be the first page

    obj_json = _make_search_request(base, query, page_state, config)

    if isinstance(obj_json, str):
        return _error_object(0, "unknown response: " + str)
    if 'errors' in obj_json:
        return obj_json

    resp_stats = {'hits': obj_json['hits'], 'took': obj_json['took']}
    items = obj_json['items']
    if 'http-headers' in obj_json:
        http_headers = obj_json['http-headers']
        if 'CMR-Scroll-Id' in http_headers and page_state['limit']>2000:
            page_state['CMR-Scroll-Id'] = http_headers['CMR-Scroll-Id']

    items = apply_filters(filters, items)
    if _continue_download(page_state):
        accumulated_took_time = page_state['took'] + resp_stats['took']
        max_allowed_time = config.get('max-time', 300000)
        if  accumulated_took_time > max_allowed_time:
            # Do not allow searches to go on forever, put an end to this and
            # return what has been found so far, but leave a log message
            logger.warning("max search time exceeded")
            return items[:page_state['limit']]
        next_page_state = _next_page_state(page_state, resp_stats['took'])
        recursive_items = search_by_page(base,
            query=query,
            filters=filters,
            page_state=next_page_state,
            config=config)
        items = items + recursive_items
    else:
        if 'CMR-Scroll-Id' in page_state and page_state['limit']>2000:
            scroll_ret = clear_scroll(page_state['CMR-Scroll-Id'], config)
            if 'errors' in scroll_ret:
                for err in scroll_ret['errors']:
                    logger.warning('Error processing scroll: %s', err)
    logger.info("Total records downloaded was %d of %d which took %dms.",
        len(items),
        resp_stats['hits'],
        resp_stats['took'])
    return items[:page_state['limit']]

# document-it: {"from":"._make_search_request"}
def experimental_search_by_page_generator(base, query = None, filters = None,
        page_state = None, config: dict = None):
    """
    WARNING: This is an experimental function, do not use in an operational
    system, this function will go away.

    This function performs searches and returns data as a list generator. Errors
    will go mostly to logs.
    """

    if page_state is None:
        page_state = create_page_state()  # must be the first page
    if config is None:
        config = {}

    obj_json = _make_search_request(base, query, page_state, config)

    if page_state['page_num'] == 1:
        logger.info('experimental_search_by_page_generator is not a supported function')

    if 'http-headers' in obj_json:
        http_headers = obj_json['http-headers']
        if 'CMR-Scroll-Id' in http_headers and page_state['limit']>2000:
            page_state['CMR-Scroll-Id'] = http_headers['CMR-Scroll-Id']

    if 'errors' in obj_json:
        errors = (obj_json['errors'])
        for err in errors:
            logger.error("Error in generator: %s.", str(err))
    else:
        items = obj_json['items']
        items = apply_filters(filters, items)
        for i in items:
            yield i

    if _continue_download(page_state):
        next_page_state = _next_page_state(page_state, 0)
        recursive_items = experimental_search_by_page_generator(base,
            query=query,
            filters=filters,
            page_state=next_page_state,
            config=config)
        yield from recursive_items
    else:
        if 'CMR-Scroll-Id' in page_state and page_state['limit']>2000:
            clear_scroll(page_state['CMR-Scroll-Id'], config)

def open_api(section):
    """Ask python to open up the API in a new browser window - unsupported!"""
    url = 'https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html'
    if section is not None:
        url = url + section
    web.open(url, new=2)

def set_logging_to(level=logging.ERROR):
    """
    Set the logging level to one of the levels 'CRITICAL', 'ERROR', 'WARNING',
    'INFO', 'DEBUG', or 'NOTSET'.
    Parameters:
        level: a value like logging.INFO or a string like 'INFO'
    """
    logger.setLevel(level)

def help_text(prefix, functions, filters):
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
