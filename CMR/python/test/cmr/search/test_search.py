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

from cmr.util import common
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
        recorded_file = tutil.resolve_full_path('../data/cmr/search/ten_results_from_ghrc.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_file)

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
        recorded_file = tutil.resolve_full_path('../data/cmr/search/one_cmr_result.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_file)

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

    def test_collection_ids_for_granules_fields(self):
        """
        Test that the function conforms to expectations by only returning the
        fields of interest
        """
        actual = coll.collection_ids_for_granules_fields({})
        expected = {}
        self.assertEqual(expected, actual)

        actual = coll.collection_ids_for_granules_fields({'unrelated':'field'})
        expected = {}
        self.assertEqual(expected, actual)

        #setup, something in umm, something in meta
        umm = {'ShortName': 'name is short',
            'provider-id':'provider-in-wrong-location'}
        meta = {'provider-id':'GHRC'}
        data = {'umm':umm, 'meta':meta}

        #test
        actual = coll.collection_ids_for_granules_fields(data)
        expected = {'ShortName': 'name is short', 'provider-id':'GHRC'}
        self.assertEqual(expected, actual)


    def test_collection_core_fields(self):
        """
        Test that the function conforms to expectations by only returning the
        fields of interest
        """
        actual = coll.collection_core_fields({})
        expected = {}
        self.assertEqual(expected, actual)

        actual = coll.collection_core_fields({'unrelated':'field'})
        expected = {}
        self.assertEqual(expected, actual)

        #setup, something in umm, something in meta
        umm = {'ShortName': 'name is short'}
        meta = {'provider-id':'GHRC', 'concept-id':'C01234-GHRC'}
        data = {'umm':umm, 'meta':meta}

        #test
        actual = coll.collection_core_fields(data)
        expected = {'ShortName': 'name is short', 'concept-id':'C01234-GHRC'}
        self.assertEqual(expected, actual)

    def test_help_full(self):
        """Test the built in help"""
        result_full = coll.help_text()
        self.assertTrue (-1<result_full.find("collection_ids_for_granules_fields"))
        self.assertTrue (-1<result_full.find("search():"))

    def test_help_less(self):
        """Test the built in help for filtering"""
        result_less = coll.help_text("_fields")
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

    @patch('urllib.request.urlopen')
    def test_logged_search(self, urlopen_mock):
        """
        Test that search still runs as expected when logging is turned on
        """
        # Setup
        recorded_file = tutil.resolve_full_path('../data/cmr/search/ten_results_from_ghrc.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_file)

        # Test
        with self.assertLogs(coll.scom.logger, level='DEBUG') as log_collector:
            coll.set_logging_to("DEBUG")
            expected = ['INFO:cmr.search.common: - POST: https://cmr.earthdata.'
                            'nasa.gov/search/collections?page_size=1',
                        'INFO:cmr.search.common:Total records downloaded was 10'
                            ' of 2038 which took 10ms.']
            coll.search({'provider':'GHRC_CLOUD'}, limit=1)
            self.assertEqual(expected, log_collector.output)

    @patch('urllib.request.urlopen')
    def test_logged_search_with_config(self, urlopen_mock):
        """
        Test that search still runs as expected when logging is turned on
        """
        # Setup
        recorded_file = tutil.resolve_full_path('../data/cmr/search/ten_results_from_ghrc.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_file)

        # Test
        with self.assertLogs(coll.scom.logger, level='DEBUG') as log_collector:
            coll.set_logging_to("DEBUG")
            expected = ['INFO:cmr.search.common:Using an Authorization token',
                        'INFO:cmr.search.common: - POST: https://cmr.earthdata.'
                            'nasa.gov/search/collections?page_size=1',
                        'INFO:cmr.search.common:Total records downloaded was 10'
                            ' of 2038 which took 10ms.']
            config = {"cmr-token": "fake-token", "authorization": "fake-token"}
            coll.search({'provider':'GHRC_CLOUD'}, config=config, limit=1)
            self.assertEqual(expected, log_collector.output)

    @patch('cmr.search.common.open_api')
    @patch('cmr.search.common.set_logging_to')
    def test_ignore_tests(self, log_mock, api_mock):
        """
        These are tests for functions which don't do much outside of the notebook
        environment. These functions are also simple wrappers for functions in
        the lower common level and should be tested there.
        """
        log_mock.return_value = "fake"
        api_mock.return_value = "fake"

        # test at least that the advertised function signature is upheld.
        # pylint: disable=E1120 # really want to check for too many parameters
        # pylint: disable=E1121 # really want to check for a required parameter
        with self.assertRaises(Exception):
            coll.open_api('#some-page-tag', "not supported")
            coll.set_logging_to()

        # most general test that could be made
        # pylint: disable=W0703 # exception is the best way to look for the unexpected
        try:
            coll.open_api()
            coll.set_logging_to(0)
        except Exception:
            self.fail("un expected error")
