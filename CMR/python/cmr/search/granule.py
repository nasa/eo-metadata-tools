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

# pylint: disable=duplicate-code

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
    umm = item.get('umm', {})
    record['GranuleUR'] = umm.get('GranuleUR')

    meta = item.get('meta', {})
    record['concept-id'] = meta.get('concept-id')
    record['revision-id'] = meta.get('revision-id')
    record['native-id'] = meta.get('native-id')
    return {key: value for key, value in record.items() if value}

def _collection_sample_limits(limits):
    """
    Assure that the limit values are not None and have reasonable values
    """
    build = lambda gran, coll : {'granule': gran, 'collection': coll}
    bound = lambda lower, value, upper : min(max(lower, value), upper)

    default_granule_limit = 10
    default_collection_limit = 20

    if limits is None:
        limit_obj = build(default_granule_limit, default_collection_limit)
    elif isinstance(limits, int):
        # assume the value is the granule sample limit
        limit_obj = build(limits, default_collection_limit)
    elif isinstance(limits, dict):
        limit_obj = limits
    elif isinstance(limits, list):
        # user may have sent in 0 or more values, first 2 are significant
        if len(limits)>1:
            # at least 2 exist
            limit_obj = build(limits[0], limits[1])
        elif len(limits)>0:
            # at least one exists
            limit_obj = build(limits[0], default_collection_limit)
        else:
            # assume none exist
            limit_obj = build(default_granule_limit, default_collection_limit)
    else:
        limit_obj = build(default_granule_limit, default_collection_limit)

    if limit_obj.get("collection") is None:
        limit_obj["collection"] = default_collection_limit

    if limit_obj.get("granule") is None:
        limit_obj["granule"] = default_granule_limit

    limit_obj["collection"] = bound(1, limit_obj["collection"], 200)
    limit_obj["granule"] = bound(1, limit_obj["granule"], 100)

    return limit_obj

def _collection_samples(collection_query, limit, config):
    """
    First step in the granule samples function is to run a collection query. Do
    not require the loading of the search.py file, call the already loaded common
    file.
    """
    just_cid = lambda obj : obj.get('meta', {}).get('concept-id')
    found_collections = scom.search_by_page("collections",
        query=collection_query,
        filters=just_cid,
        page_state=scom.create_page_state(limit=limit),
        config=config)
    return found_collections[:limit]

def _granule_samples(found_collections, filters, limit, config):
    """
    Second step in the granule samples function is to run a granule query based
    on the results of the _collection_samples() search.
    """
    found_granules = []
    for concept in found_collections:
        query = {"concept_id": concept}
        granules = search(query, filters=filters, limit=limit, config=config)
        found_granules.extend(granules)
    return found_granules[:len(found_collections)*limit]

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
def search(query, filters = None, limit = None, config: dict = None):
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

def sample_by_collections(collection_query, filters = None, limits = None, config: dict = None):
    """
    Perform a compound search looking for granules based on the results of a
    collection search. First find a list of collections using a supplied collection
    query, then take the resulting collection IDs and perform a granule search
    with them. Granule samples are then returned from many of the collections.

    Parameters:
        collection_query(dictionary) : a collection query
        filters(list): a list of filter lambdas which taken in a row and return and row
        limits: an int, a list of 0 to 2 int values, or a dictionary, None values will be asasumed
            list: [granule limit, collection limit]
            dictionary: {'granule': None, 'collection': None}
        config (dictionary): configuration settings
    """

    # prep work
    limit_obj = _collection_sample_limits(limits)
    max_limit = limit_obj["granule"] * limit_obj["collection"]

    # searches
    found_collections = _collection_samples(collection_query, limit_obj["collection"], config)
    found_granules = _granule_samples(found_collections, filters, limit_obj["granule"], config)

    # return results
    return found_granules[:max_limit]

# document-it: {"from":"cmr.search.common.experimental_search_by_page_generator"}
def experimental_search_generator(query, filters = None, limit = None, config: dict = None):
    """
    WARNING: This is an experimental function, do not use in an operational
    system, this function will go away.

    This function performs searches and returns data as a list generator. Errors
    will go to logs. A list generator may be more performant on large datasets,
    but some experimenting is needed.
    Parameters:
        query (dictionary): required, CMR search parameters
        filters (list): column filter lambdas
        limit (int): number from 1 to 100000
        config (dictionary): configuration settings
    Returns:
        JSON results from CMR
    """
    page_state = scom.create_page_state(limit=limit)
    found_items = scom.experimental_search_by_page_generator("granules",
        query=query,
        filters=filters,
        page_state=page_state,
        config=config)
    yield from found_items

def open_api(section = '#granule-search-by-parameters'):
    """
    Ask python to open up the API in a new browser window
    Parameters:
        selection(string): HTML Anchor Tag, default is #granule-search-by-parameters
    """
    scom.open_api(section)

def set_logging_to(level):
    """
    Set the logging level to the stated value. Any of the standard logging level
    as stated in https://docs.python.org/3/howto/logging.html#when-to-use-logging
    can be used here. These include: DEBUG, INFO, WARNING, ERROR, and CRITICAL
    Parameters:
        level: a value like logging.INFO
    """
    scom.set_logging_to(level)

def help_text(contains: str = ""):
    """Return help for the public functions in the Granule api"""
    functions = [apply_filters,
        open_api,
        help_text,
        search,
        set_logging_to]
    filters = [all_fields,
        concept_id_fields,
        drop_fields,
        granule_core_fields,
        meta_fields,
        umm_fields]
    return scom.help_text(contains, functions, filters)
