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
        filters - a list of filter lambdas
        limit - Enum limiting the number of records returned
        options - configurations

Queries can be modified to support sorting by using two functions which taken in
a query dictionary and modify it to include the sorting instructions.
    sort_by() : adds the sort key to the query
        query - original query
        Sort (enum) - with values supported by CMR
    descending(): modify an existing sort key to be in reverse, or set it if provided
        query - original query
        Sort (enum) - Optional, with values supported by CMR

Limits are handled with the Limit enum but integers can also be used. The enum
contains some common values used with CMR, such as the default page size.

More information can be found at:
https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html

"""

from enum import Enum, IntEnum
import sys

import cmr.search.common as scom
#import cmr.util.logging as log

# ******************************************************************************
# Enums

class CollectionLimit(IntEnum):
    """
    Enum for representing CMR response limits ; used restrict the number of
    records returned by CMR
    """
    UNLIMITED = -1      # keep paging no matter what
    NONE = 0            # Don't actually need data, headers are more important.
    ONE = 1             # I'm feeling Lucky...
    TEN = 10            # Half the CMR Default
    DEFAULT = 20        # The CMR Default
    HUNDRED = 100       # A nice human number
    KILO = 1024         # An even amount, one kilo of metadata
    PAGE = 2000         # The max CMR will give in a page
    COLLECTIONS = 30000  # estimated to be all the collections
    MAX = sys.maxsize   # Largest Python will count to

class CollectionSort(Enum):
    """
    Enum for representing the different sort options available in CMR
    """
    ENTRY_TITLE = 'entry_title'

    """ Alias for entry_title"""
    DATASET_ID = 'dataset_id'
    SHORT_NAME = 'short_name'
    ENTRY_ID = 'entry_id'
    START_DATE = 'start_date'
    END_DATE = 'end_date'
    PLATFORM = 'platform'
    INSTRUMENT = 'instrument'
    SENSOR = 'sensor'
    PROVIDER = 'provider'
    REVISION_DATE = 'revision_date'
    SCORE = 'score' # document relevance score, defaults to descending.

    """
    Sorts collections by whether they have granules or not. Collections with
    granules are sorted before collections without granules.
    """
    HAS_GRANULES = 'has_granules'

    """
    Sorts collections by whether they have granules or they are tagged as a CWIC
    collection. Collections with granules or are CWIC tagged are sorted before
    collections without granules or a CWIC tag.
    """
    HAS_GRANULES_OR_CWIC = 'has_granules_or_cwic'

    """
    Sorts collection by usage. The usage score comes from the EMS metrics, which
    are ingested into the CMR.
    """
    USAGE_SCORE = 'usage_score'

    ONGOING = 'ongoing'

# ******************************************************************************
# filter function lambdas

def filter_none(item):
    """Pass through, do no filtering - is this needed outside of testing?"""
    return scom.filter_none(item)
def filter_meta(item):
    """Return only the the meta objects"""
    return scom.filter_meta(item)
def filter_umm(item):
    """Return only the UMM part of the data"""
    return scom.filter_umm(item)
def filter_concept_ids(item):
    """extract only fields that are used to identify a record"""
    return scom.filter_concept_ids(item)
def filter_drop(key):
    """drop a key from a dictionary"""
    return scom.filter_drop(key)

def filter_ids(item):
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

def filter_gids(item):
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

def sort_by(params, sort):
    """
    Add sorting to the CMR parameters. This will change the params.
    Parameters:
        params(dictionary): the CMR parameters to add to
        sort(Sort): a value from the Sort enum
    Returns:
        params - can be chained
    """
    return scom.sort_by(CollectionSort, params, sort)
def descending(params, sort=None):
    """
    Add reverses the sorting in the CMR parameters. This will change the params.
    Parameters:
        params(dictionary): the CMR parameters to add to
        sort(Sort): Optional, will set the value from the Sort enum
    Returns:
        params - can be chained
    """
    return scom.descending(CollectionSort, params, sort)

def search(query=None, filters=None, limit=None, options=None):
    """
    Search and return all records
    """
    if limit is None:
        limit = CollectionLimit.DEFAULT
    if isinstance(limit, int):
        try:
            limit = CollectionLimit(limit)
        except ValueError:
            limit = int(limit)

    page_state = scom.create_page_state(limit=limit)
    found_items = scom.search_by_page("collections",
        query=query,
        filters=filters,
        page_state=page_state,
        options=options)
    return found_items

def open_api(section='#collection-search-by-parameters'):
    """Ask python to open up the API in a new browser window"""
    scom.open_api(section)

def print_help(prefix=""):
    """
    Built in help - prints out the public function names for the collection object for the token API
    Parameters:
        filter(string): filters out functions beginning with this text, defaults to all
    """
    functions = [print_help, search]
    filters = [filter_concept_ids, filter_gids, filter_drop, filter_ids,
        filter_meta, filter_none, filter_umm]
    return scom.print_help(prefix, functions, filters)
