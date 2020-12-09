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
Test cases for the cmr.search.search module
Author: thomas.a.cherry@nasa.gov - NASA
Created: 2020-10-15
"""

from unittest.mock import patch
import unittest

import test.cmr as tutil

import cmr.util.common as common
import cmr.search.collection as coll

# ******************************************************************************

def valid_cmr_response(file, status=200):
    """return a valid login response"""
    json_response = common.read_file(file)
    return tutil.MockResponse(json_response, status=status)

class TestSearch(unittest.TestCase):
    """Test suit for Search API"""

    # **********************************************************************
    # Util methods

    # **********************************************************************
    # Tests

    @patch('urllib.request.urlopen')
    def test_limited_search(self, urlopen_mock):
        """
        Test that the limit parameter will not allow more data to be returned.
        CMR may return more data on the last page if a page value is specified.
        For this test, 10 results are returned and the API will opt to return
        fewer to the caller
        """
        # Setup
        recorded_data_file = 'test/data/cmr/search/ten_results_from_ghrc.json'
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)

        # tests
        for index in [1,2,5,10]:
            result = coll.search({'provider':'GHRC_CLOUD'}, limit=index)
            self.assertEqual(index, len(result))

    @patch('urllib.request.urlopen')
    def test_search(self, urlopen_mock):
        """
        def search(query=None, filters=None, limit=None, config=None):
        """
        # Setup
        recorded_data_file = 'test/data/cmr/search/one_cmr_result.json'
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)

        full_result = coll.search({'provider':'SEDAC'}, limit=1)
        self.assertEqual(1, len(full_result))

        # Unfiltered Test
        unfiltered_result = coll.search({'provider':'SEDAC'},
            filters=[coll.all_fields],
            limit=1)
        self.assertEqual(full_result, unfiltered_result)

        # Meta filter Test
        meta_results = coll.search({'provider':'SEDAC'},
            filters=[coll.meta_fields],
            limit=1)
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
            filters=[coll.umm_fields],
            limit=1)
        expected = '2000 Pilot Environmental Sustainability Index (ESI)'
        self.assertEqual(expected, umm_results[0]['EntryTitle'])
        self.assertEqual(28, len(umm_results[0].keys()))

        # Collection ID Filter Test
        cid_results = coll.search({'provider':'SEDAC'},
            filters=[coll.concept_id_fields],
            limit=1)
        expected = [{'concept-id': 'C179001887-SEDAC'}]
        self.assertEqual(expected, cid_results)

        # Drop Filter Test
        drop_results = coll.search({'provider':'SEDAC'},
            filters=[coll.meta_fields,
                coll.drop_fields('has-temporal-subsetting'),
                coll.drop_fields('revision-date'),
                coll.drop_fields('has-spatial-subsetting')],
            limit=1)
        expected = [{'concept-id': 'C179001887-SEDAC'}]
        meta_count = len(meta_results[0].keys()) #from test above
        drop_count = len(drop_results[0].keys())
        self.assertEqual(3, meta_count-drop_count)

        #IDs Filter Test
        ids_results = coll.search({'provider':'SEDAC'},
            filters=[coll.collection_core_fields],
            limit=1)
        expected = [{'concept-id': 'C179001887-SEDAC',
            'ShortName': 'CIESIN_SEDAC_ESI_2000',
            'Version': '2000.00',
            'EntryTitle': '2000 Pilot Environmental Sustainability Index (ESI)'}]
        self.assertEqual(expected, ids_results)

        # Granule IDs Filter Tests
        gids_results = coll.search({'provider':'SEDAC'},
            filters=[coll.collection_ids_for_granules_fields],
            limit=1)
        expected = [{'provider-id': 'SEDAC',
            'concept-id': 'C179001887-SEDAC',
            'ShortName': 'CIESIN_SEDAC_ESI_2000',
            'Version': '2000.00',
            'EntryTitle': '2000 Pilot Environmental Sustainability Index (ESI)'}]
        self.assertEqual(expected, gids_results)

    def test_help_full(self):
        """Test the built in help"""
        result_full = coll.print_help()
        self.assertTrue (-1<result_full.find("collection_ids_for_granules_fields"))
        self.assertTrue (-1<result_full.find("search():"))

    def test_help_less(self):
        """Test the built in help for filtering"""
        result_less = coll.print_help("_fields")
        self.assertTrue (-1<result_less.find("collection_ids_for_granules_fields"))
        self.assertFalse (-1<result_less.find("search():"))

    def test_apply_filter(self):
        """Test that apply filters function can be used to strip items out of the data"""
        data = [{'a':'11', 'b':'21', 'c':'31'}, {'a':'12', 'b':'22', 'c':'32'}]
        result = coll.apply_filters([coll.drop_fields('a'), coll.drop_fields('b')], data)
        expected = [{'c': '31'}, {'c': '32'}]
        self.assertEqual (expected, result)

    # Ignore this so that an example of how to run the code can be documented
    # pylint: disable=R0201
    def _test_live_search(self):
        """
        Make a live call to CMR, this is not normally included in the test suite.
        Turn it on for doing some local tests
        """
        params = {}
        config = {}
        #params["provider"] = "SEDAC"
        params['keyword'] = 'salt'
        results = coll.search(query=params,
            filters=[coll.collection_core_fields, coll.drop_fields('EntryTitle')],
            limit=None,
            config=config)
        for i in results:
            print (i)
