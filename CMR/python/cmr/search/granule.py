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
A Library for building and requesting CMR granule searches
date: 2020-11-23
since: 0.0

A simple search interface for CMR. Use the search() function to perform searches.
This function can handle any query parameter which is supported by the CMR.

    search()
        query - a dictionary of CMR parameters
        filters - a list of result filter lambdas
        limit - int limiting the number of records returned
        config - configurations

More information can be found at:
https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html
"""

import cmr.search.common as scom

# ******************************************************************************
# filter function lambdas

def all_fields(item):
    """
    Makes no change to the item, passes through. Used primarily as an example
    and for testing the filter workflow
    """
    return scom.all_fields(item)
def meta_fields(item):
    """Return only the the meta objects"""
    return scom.meta_fields(item)
def umm_fields(item):
    """Return only the UMM part of the data"""
    return scom.umm_fields(item)
def concept_id_fields(item):
    """Extract only fields that are used to identify a record"""
    return scom.concept_id_fields(item)
def drop_fields(key):
    """Drop a key from a dictionary"""
    return scom.drop_fields(key)

def granule_core_fields(item):
    """Extract only fields that are used to identify a record"""
    record = {}
    if 'umm' in item:
        umm = item['umm']
        record['GranuleUR'] = umm['GranuleUR']
    if 'meta' in item:
        meta = item['meta']
        record['concept-id'] = meta['concept-id']
        record['revision-id'] = meta['revision-id']
        record['native-id'] = meta['native-id']
    if len(record.keys())>0:
        return record
    return item

# ******************************************************************************
# public search functions

def apply_filters(filters, items):
    """
    Apply all the filters on the downloaded data
    Parameters:
        filters(list): a list of filter lambdas which taken in a row and return and row
        items(list): list of records from CMR
    Returns:
        Filtered data
    """
    return scom.apply_filters(filters, items)

def search(query, filters=None, limit=None, config=None):
    """
    Search and return all records
    Parameters:
        query (dictionary): required, CMR search parameters
        filters (list): column filter lambdas
        limit (int): number from 1 to 100000
        config (dictionary): configuration settings
    Returns:
        JSON results from CMR
    """
    page_state = scom.create_page_state(limit=limit)
    found_items = scom.search_by_page("granules",
        query=query,
        filters=filters,
        page_state=page_state,
        config=config)
    return found_items

def open_api(section='#granule-search-by-parameters'):
    """
    Ask python to open up the API in a new browser window
    Parameters:
        selection(string): HTML Anchor Tag, default is #granule-search-by-parameters
    """
    scom.open_api(section)

def print_help(contains=""):
    """Return help for the public functions in the Granule api"""
    functions = [apply_filters, open_api, print_help, search]
    filters = [granule_core_fields, drop_fields, concept_id_fields, meta_fields,
        umm_fields, all_fields]
    return scom.print_help(contains, functions, filters)
