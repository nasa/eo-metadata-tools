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
A Library for building and requesting CMR collection searches
date: 2020-11-23
since: 0.0

A simple search interface for CMR. Use the search() function to perform searches.
This function can handle any query parameter which is supported by the CMR.

    search()
        query - a dictionary of CMR parameters
        filters - a list of result filter lambdas
        limit - int, limiting the number of records returned
        config - configurations

More information can be found at:
https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html

"""

import cmr.search.common as scom

# ******************************************************************************
# filter function lambdas

def all_fields(item):
    """Pass through, do no filtering - is this needed outside of testing?"""
    return scom.all_fields(item)
def meta_fields(item):
    """Return only the the meta objects"""
    return scom.meta_fields(item)
def umm_fields(item):
    """Return only the UMM part of the data"""
    return scom.umm_fields(item)
def concept_id_fields(item):
    """extract only fields that are used to identify a record"""
    return scom.concept_id_fields(item)
def drop_fields(key):
    """drop a key from a dictionary"""
    return scom.drop_fields(key)

def collection_core_fields(item):
    """Extract only fields that are used to identify a record"""
    if 'umm' in item:
        umm = item['umm']
    else:
        return item
    if 'meta' in item:
        meta = item['meta']
    else:
        return item
    record = {'concept-id': meta['concept-id'],
        'ShortName': umm['ShortName'],
        'Version': umm['Version'],
        'EntryTitle': umm['EntryTitle']}
    return record

def collection_ids_for_granules_fields(item):
    """Extract only the fields that are of interest to doing a granule search"""
    if 'umm' in item:
        umm = item['umm']
    else:
        return item
    if 'meta' in item:
        meta = item['meta']
    else:
        return item
    provider_id = meta['provider-id']
    collection_concept_id = meta['concept-id']
    short_name = umm['ShortName']
    version = umm['Version']
    entry_title = umm['EntryTitle']
    record = {'provider-id': provider_id,
        'concept-id': collection_concept_id,
        'ShortName': short_name,
        'Version': version,
        'EntryTitle': entry_title}
    return record

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

def search(query=None, filters=None, limit=None, config=None):
    """
    Search and return all records
    """
    page_state = scom.create_page_state(limit=limit)
    found_items = scom.search_by_page("collections",
        query=query,
        filters=filters,
        page_state=page_state,
        config=config)
    return found_items

def open_api(section='#collection-search-by-parameters'):
    """Ask python to open up the API in a new browser window"""
    scom.open_api(section)

def print_help(contains=""):
    """
    Built in help - prints out the public function names for the collection object for the token API
    Parameters:
        filter(string): filters out functions beginning with this text, defaults to all
    """
    functions = [apply_filters, open_api, print_help, search]
    filters = [collection_ids_for_granules_fields, collection_core_fields,
        drop_fields, concept_id_fields, umm_fields, meta_fields, all_fields]
    return scom.print_help(contains, functions, filters)
