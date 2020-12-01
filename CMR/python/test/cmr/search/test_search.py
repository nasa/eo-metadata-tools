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
Test cases for the cmr.auth package
Author: thomas.a.cherry@nasa.gov - NASA
Created: 2020-10-15
"""

#from unittest.mock import Mock
from unittest.mock import patch
import unittest

import test.cmr as tutil

#import cmr.auth.token as token
#import cmr.auth.login as login
import cmr.util.common as common
import cmr.search.collection as coll

# ******************************************************************************

def valid_cmr_response(file):
    """return a valid login response"""
    json_response = common.read_file(file)
    return tutil.MockResponse(json_response)

class TestSearch(unittest.TestCase):
    """Test suit for Search API"""

    # **********************************************************************
    # Util methods

    # **********************************************************************
    # Tests

    def test_sort_by(self):
        """Check that the sort by attribute is added correctly"""

        # Send None you get None
        result = coll.sort_by(None, None)
        self.assertEqual(None, result)

        result = coll.sort_by(None, coll.CollectionSort.SHORT_NAME)
        self.assertEqual(None, result)

        result = coll.sort_by({}, None)
        self.assertEqual({}, result)

        # Send a dictionary that is filled
        result = coll.sort_by({}, coll.CollectionSort.SHORT_NAME)
        self.assertEqual('short_name', result['sort_key'])

        # Send a dictionary with a descending
        result = coll.sort_by({'sort_key':'-short_name'}, coll.CollectionSort.SHORT_NAME)
        self.assertEqual('short_name', result['sort_key'])

        # Call it twice
        pass1 = coll.sort_by({}, coll.CollectionSort.SHORT_NAME)
        result = coll.sort_by(pass1, coll.CollectionSort.SHORT_NAME)
        self.assertEqual('short_name', result['sort_key'])

        # Send a dictionary with stuff in it already
        result = coll.sort_by({'a': "one", 'b': 'two'}, coll.CollectionSort.SHORT_NAME)
        self.assertEqual('short_name', result['sort_key'])
        self.assertEqual('one', result['a'])
        self.assertEqual('two', result['b'])

    def test_descending(self):
        """Check that the sort by attribute is added correctly"""

        # Send None you get None
        result = coll.descending(None, None)
        self.assertEqual(None, result)
        result = coll.descending(None, coll.CollectionSort.SHORT_NAME)
        self.assertEqual(None, result)
        result = coll.descending({}, None)
        self.assertEqual({}, result)

        # Send a dictionary and it is filled
        result = coll.descending({}, coll.CollectionSort.SHORT_NAME)
        self.assertEqual('-short_name', result['sort_key'])

        # Send a dictionary with a descending
        result = coll.descending({'sort_key':'short_name'}, coll.CollectionSort.SHORT_NAME)
        self.assertEqual('-short_name', result['sort_key'])

        # Call it twice
        pass1 = coll.descending({}, coll.CollectionSort.SHORT_NAME)
        result = coll.descending(pass1, coll.CollectionSort.SHORT_NAME)
        self.assertEqual('-short_name', result['sort_key'])

        # Send a dictionary with stuff in it already
        result = coll.descending({'a': "one", 'b': 'two'}, coll.CollectionSort.SHORT_NAME)
        self.assertEqual('-short_name', result['sort_key'])
        self.assertEqual('one', result['a'])
        self.assertEqual('two', result['b'])

    @patch('urllib.request.urlopen')
    def test_search(self, urlopen_mock):
        """
        def search(query=None, filters=None, limit=None, options=None):
        """
        # Setup
        urlopen_mock.return_value = valid_cmr_response('test/data/cmr/search/one_cmr_result.json')

        full_result = coll.search({'provider':'SEDAC'}, limit=coll.CollectionLimit.ONE)
        self.assertEqual(1, len(full_result))

        # Unfiltered Test
        unfiltered_result = coll.search({'provider':'SEDAC'},
            filters=[coll.filter_none],
            limit=coll.CollectionLimit.ONE)
        self.assertEqual(full_result, unfiltered_result)

        # Meta filter Test
        meta_results = coll.search({'provider':'SEDAC'},
            filters=[coll.filter_meta],
            limit=coll.CollectionLimit.ONE)
        expected = [{'revision-id': 31,
            'deleted': False,
            'format': 'application/dif10+xml',
            'provider-id': 'SEDAC',
            'user-id': 'mhansen',
            'has-formats': False,
            'has-spatial-subsetting': False,
            'native-id': '2000 Pilot Environmental Sustainability Index (ESI)',
            'has-transforms': False,
            'has-variables': False,
            'concept-id': 'C179001887-SEDAC',
            'revision-date': '2019-07-26T18:37:52.861Z',
            'granule-count': 0,
            'has-temporal-subsetting': False,
            'concept-type': 'collection'}]
        self.assertEqual(expected, meta_results)

        # UMM filter Test
        umm_results = coll.search({'provider':'SEDAC'},
            filters=[coll.filter_umm],
            limit=coll.CollectionLimit.ONE)
        expected = '2000 Pilot Environmental Sustainability Index (ESI)'
        self.assertEqual(expected, umm_results[0]['EntryTitle'])
        self.assertEqual(28, len(umm_results[0].keys()))

        # Collection ID Filter Test
        cid_results = coll.search({'provider':'SEDAC'},
            filters=[coll.filter_concept_ids],
            limit=coll.CollectionLimit.ONE)
        expected = [{'concept-id': 'C179001887-SEDAC'}]
        self.assertEqual(expected, cid_results)

        # Drop Filter Test
        drop_results = coll.search({'provider':'SEDAC'},
            filters=[coll.filter_meta,
                coll.filter_drop('has-temporal-subsetting'),
                coll.filter_drop('revision-date'),
                coll.filter_drop('has-spatial-subsetting')],
            limit=coll.CollectionLimit.ONE)
        expected = [{'concept-id': 'C179001887-SEDAC'}]
        meta_count = len(meta_results[0].keys()) #from test above
        drop_count = len(drop_results[0].keys())
        self.assertEqual(3, meta_count-drop_count)

        #IDs Filter Test
        ids_results = coll.search({'provider':'SEDAC'},
            filters=[coll.filter_ids],
            limit=coll.CollectionLimit.ONE)
        expected = [{'concept-id': 'C179001887-SEDAC',
            'ShortName': 'CIESIN_SEDAC_ESI_2000',
            'Version': '2000.00',
            'EntryTitle': '2000 Pilot Environmental Sustainability Index (ESI)'}]
        self.assertEqual(expected, ids_results)

        # Granule IDs Filter Tests
        gids_results = coll.search({'provider':'SEDAC'},
            filters=[coll.filter_gids],
            limit=coll.CollectionLimit.ONE)
        expected = [{'provider-id': 'SEDAC',
            'concept-id': 'C179001887-SEDAC',
            'ShortName': 'CIESIN_SEDAC_ESI_2000',
            'Version': '2000.00',
            'EntryTitle': '2000 Pilot Environmental Sustainability Index (ESI)'}]
        self.assertEqual(expected, gids_results)

    def test_help_full(self):
        """Test the built in help"""
        result_full = coll.print_help()
        self.assertTrue (-1<result_full.find("filter_gids"))
        self.assertTrue (-1<result_full.find("search():"))

    def test_help_less(self):
        """Test the built in help for filtering"""
        result_less = coll.print_help("filter_")
        self.assertTrue (-1<result_less.find("filter_gids"))
        self.assertFalse (-1<result_less.find("search():"))

    # Ignore this so that an example of how to run the code can be documented
    # pylint: disable=R0201
    def _test_live_search(self):
        """
        Make a live call to CMR, this is not normally included in the test suite.
        Turn it on for doing some local tests
        """
        params = {}
        options = {}
        #params["provider"] = "SEDAC"
        params['keyword'] = 'salt'
        results = coll.search(query=params,
            filters=[coll.filter_ids, coll.filter_drop('EntryTitle')],
            limit=None,
            options=options)
        for i in results:
            print (i)
