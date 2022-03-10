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
A Library for requesting CMR Provider Names
date: 2022-03-09
since: 0.1

A provider search for CMR. Use the search() function to lookup all the providers.
search_by_id() can be used to return only providers matching a regular expression.
"""
# pylint: disable=duplicate-code

import re

import cmr.util.common as com
import cmr.util.network as net
import cmr.search.common as scom

# ******************************************************************************
# filter function lambdas

# document-it: {"from":"cmr.search.common.search_by_page"}
def search(config: dict = None):
    """
    Search for and return providers, optional filter them
    Parameters:
        config - configurations
    Return:
        JSON list of providers on success, Map with 'errors' otherwise
    """
    config = com.always(config)

    url = scom.cmr_basic_url(endpoint='ingest', base="providers", config=config)

    response = net.get(url)

    if 'errors' in response:
        return response #let caller know about the errors
    provider_list = []
    for item in response.get('items', []):
        # filter out deprecated fields
        item.pop('cmr-only')
        item.pop('small')
        provider_list.append(item)
    return provider_list

def search_by_id(query:str, config: dict = None):
    """
    Search for providers and filter them down with a Regular expression
    Parameters:
        filter: RegExp string to match provider names
        config: configurations
    Return:
        JSON list of providers on success, Map with 'errors' otherwise
    """
    response = search(config=config)

    if 'errors' in response:
        return response #let caller know about the errors
    if query is None:
        return response
    query = query.strip()
    if len(query)<1:
        return response

    try:
        expression = re.compile(query, re.IGNORECASE)
    except re.error:
        return {'errors':['Regular Expression is invalid and could not compile']}

    # there is data and a valid filter, subset the data with the filter
    found = []
    for provider in response:
        if expression.match(provider.get('provider-id')):
            found.append(provider)
    return found

def set_logging_to(level):
    """
    Set the logging level to the stated value. Any of the standard logging level
    as stated in https://docs.python.org/3/howto/logging.html#when-to-use-logging
    can be used here. These include: DEBUG, INFO, WARNING, ERROR, and CRITICAL
    Parameters:
        level: a value like logging.INFO
    """
    scom.set_logging_to(level)

def open_api(section = '#collection-search-by-parameters'):
    """Ask python to open up the API in a new browser window"""
    scom.open_api(section)

def help_text(contains: str = ""):
    """
    Built in help - prints out the public function names for the collection object for the token API
    Parameters:
        filter(string): filters out functions beginning with this text, defaults to all
    """
    functions = [search,
        search_by_id,
        help_text,
        set_logging_to]
    filters = []
    return scom.help_text(contains, functions, filters)
