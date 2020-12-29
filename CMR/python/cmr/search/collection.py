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

def collection_core_fields(item):
    """Extract only fields that are used to identify a record"""
    record = {}
    # Define umm
    umm = item.get('umm', {})
    record['ShortName'] = umm.get('ShortName')
    record['Version'] = umm.get('Version')
    record['EntryTitle'] = umm.get('EntryTitle')
    # Define meta
    meta = item.get('meta', {})
    record['concept-id'] = meta.get('concept-id')
    return {key: value for key, value in record.items() if value}

def collection_ids_for_granules_fields(item: object):
    """Extract only the fields that are of interest to doing a granule search"""
    record = {}
    # Define umm
    umm = item.get('umm', {})
    record['ShortName'] = umm.get('ShortName')
    record['Version'] = umm.get('Version')
    record['EntryTitle'] = umm.get('EntryTitle')
    # Define meta
    meta = item.get('meta', {})
    record['provider-id'] = meta.get('provider-id')
    record['concept-id'] = meta.get('concept-id')
    return {key: value for key, value in record.items() if value}

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

# document-it: {"from":"cmr.search.common.search_by_page"}
def search(query=None, filters=None, limit=None, config:dict = None):
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

def set_logging_to(level):
    """
    Set the logging level to the stated value. Any of the standard logging level
    as stated in https://docs.python.org/3/howto/logging.html#when-to-use-logging
    can be used here. These include: DEBUG, INFO, WARNING, ERROR, and CRITICAL
    Parameters:
        level: a value like logging.INFO
    """
    scom.set_logging_to(level)

def open_api(section='#collection-search-by-parameters'):
    """Ask python to open up the API in a new browser window"""
    scom.open_api(section)

def help_text(contains:str = ""):
    """
    Built in help - prints out the public function names for the collection object for the token API
    Parameters:
        filter(string): filters out functions beginning with this text, defaults to all
    """
    functions = [apply_filters,
        open_api,
        help_text,
        search,
        set_logging_to]
    filters = [all_fields,
        collection_core_fields,
        collection_ids_for_granules_fields,
        concept_id_fields,
        drop_fields,
        meta_fields,
        umm_fields]
    return scom.help_text(contains, functions, filters)
