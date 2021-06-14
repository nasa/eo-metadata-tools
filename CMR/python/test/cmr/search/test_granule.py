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
Test cases for the cmr.search.granule package
Author: thomas.a.cherry@nasa.gov - NASA
Created: 2020-12-01
"""

#from unittest.mock import Mock
import os
from unittest.mock import patch
import unittest
from functools import partial

import test.cmr as tutil

import cmr.util.common as common
import cmr.search.granule as gran

# ******************************************************************************

# pylint: disable=W0212 # there is nothing wrong with testing private functions

def valid_cmr_response(file):
    """Return a valid login response"""
    json_response = common.read_file(file)
    return tutil.MockResponse(json_response)

class TestSearch(unittest.TestCase):
    """Test suit for Search API"""

    # **********************************************************************
    # Util methods

    # **********************************************************************
    # Tests

    @patch('urllib.request.urlopen')
    def test_search(self, urlopen_mock):
        """
        def search(query=None, filters=None, limit=None, options=None):
        """
        # Setup
        urlopen_mock.return_value = valid_cmr_response(
            os.path.join (os.path.dirname (__file__),
                '../../data/cmr/search/one_granule_cmr_result.json')
        )

        # Basic
        full_result = gran.search({'provider':'SEDAC'}, limit=1)
        self.assertEqual(1, len(full_result))

        # Unfiltered Test
        unfiltered_result = gran.search({'provider':'SEDAC'},
            filters=[gran.all_fields],
            limit=1)
        self.assertEqual(full_result, unfiltered_result)

        # Meta filter Test
        meta_results = gran.search({'provider':'SEDAC'},
            filters=[gran.meta_fields],
            limit=1)
        expected = [{'concept-type': 'granule',
            'concept-id': 'G1527288030-SEDAC',
            'revision-id': 2,
            'native-id': 'urbanspatial-hist-urban-pop-3700bc-ad2000-xlsx.xlsx',
            'provider-id': 'SEDAC',
            'format': 'application/echo10+xml',
            'revision-date': '2020-08-11T13:54:58.567Z'}]
        self.assertEqual(expected, meta_results)

        # UMM filter Test
        umm_results = gran.search({'provider':'SEDAC'},
            filters=[gran.umm_fields],
            limit=1)
        expected = 'urbanspatial-hist-urban-pop-3700bc-ad2000-xlsx.xlsx'
        self.assertEqual(expected, umm_results[0]['GranuleUR'])
        self.assertEqual(11, len(umm_results[0].keys()))

        # Collection ID Filter Test
        cid_results = gran.search({'provider':'SEDAC'},
            filters=[gran.concept_id_fields],
            limit=1)
        expected = [{'concept-id': 'G1527288030-SEDAC'}]
        self.assertEqual(expected, cid_results)

        # Drop Filter Test
        drop_results = gran.search({'provider':'SEDAC'},
            filters=[gran.meta_fields,
                gran.drop_fields('concept-type'),
                gran.drop_fields('revision-date'),
                gran.drop_fields('format')],
            limit=1)
        expected = [{'concept-id': 'G1527288030-SEDAC'}]
        meta_count = len(meta_results[0].keys()) #from test above
        drop_count = len(drop_results[0].keys())
        self.assertEqual(3, meta_count-drop_count)

        #IDs Filter Test
        ids_results = gran.search({'provider':'SEDAC'},
            filters=[gran.granule_core_fields],
            limit=1)
        expected = [{'concept-id': 'G1527288030-SEDAC',
            'revision-id': 2,
            'native-id': 'urbanspatial-hist-urban-pop-3700bc-ad2000-xlsx.xlsx',
            'GranuleUR': 'urbanspatial-hist-urban-pop-3700bc-ad2000-xlsx.xlsx'}]
        self.assertEqual(expected, ids_results)

    def test_granule_core_fields(self):
        """
        Test that the function conforms to expectations by only returning the
        fields of interest
        """
        actual = gran.granule_core_fields({})
        expected = {}
        self.assertEqual(expected, actual)

        actual = gran.granule_core_fields({'unrelated':'field'})
        expected = {}
        self.assertEqual(expected, actual)

        #setup, something in umm, something in meta
        umm = {'GranuleUR': 'Some UR for Granules',
            'concept-id':'concept-id-in-wrong-location'}
        meta = {'concept-id':'G01234-GHRC', 'revision-id':'1', 'ignore':'this'}
        data = {'umm':umm, 'meta':meta}

        #test
        actual = gran.granule_core_fields(data)
        expected = {'GranuleUR': 'Some UR for Granules',
            'concept-id':'G01234-GHRC',
            'revision-id':'1'}
        self.assertEqual(expected, actual)

    def test_apply_filter(self):
        """Test that apply filters function can be used to strip items out of the data"""
        data = [{'a':'11', 'b':'21', 'c':'31'}, {'a':'12', 'b':'22', 'c':'32'}]
        result = gran.apply_filters([gran.drop_fields('a'), gran.drop_fields('b')], data)
        expected = [{'c': '31'}, {'c': '32'}]
        self.assertEqual (expected, result)

    def test_help_full(self):
        """Test the built in help"""
        result_full = gran.help_text()
        self.assertTrue (-1<result_full.find("granule_core_fields"))
        self.assertTrue (-1<result_full.find("search():"))

    def test_help_less(self):
        """Test the built in help for filtering"""
        result_less = gran.help_text("_fields")
        self.assertTrue (-1<result_less.find("granule_core_fields"))
        self.assertFalse (-1<result_less.find("search():"))

    # ##################################
    # Granule sample Tests

    def coll_sam_lim_helper(self, expected, inputs, msg):
        """
        Helper method to do the actual testing of one use case of _collection_sample()
        """

        limits = gran._collection_sample_limits([inputs[0], inputs[1]])
        actual = [limits["granule"], limits["collection"]]
        self.assertEqual(expected, actual, msg)

    def test_collection_sample_limits(self):
        """
        Test the internal limit function to make sure it returns the correct
        values for global limits, collection limits, and granule limits depending
        on what is passed in.
        """
        self.coll_sam_lim_helper([10, 20], [None, None], "None")
        self.coll_sam_lim_helper([10, 32], [None, 32], "Collection Limit Specified")
        self.coll_sam_lim_helper([32, 20], [32, None], "Granule Limit Specified")
        self.coll_sam_lim_helper([32, 32], [32, 32], "Granule & Collection Limit Specified")

        self.coll_sam_lim_helper([32, 1], [32, -32], "Bad collection limit")
        self.coll_sam_lim_helper([1, 32], [-32, 32], "Bad granule limit")
        self.coll_sam_lim_helper([1, 1], [-32, -32], "Bad collection and granule limit")

    @patch('urllib.request.urlopen')
    def test_compound_search_collection(self, urlopen_mock):
        """
        Test the compound test works
        """
        # Setup
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/cmr/search/ten_results_from_ghrc.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)

        # tests
        for limit in [1,2,5,10]:
            result = gran._collection_samples({'provider':'GHRC_CLOUD'}, limit, {})
            self.assertEqual(limit, len(result), "limit check")
        # last call was the full 10, use that going forward
        self.assertEqual(['C179003030-ORNL_DAAC',
            'C179002914-ORNL_DAAC',
            'C1000000000-ORNL_DAAC',
            'C1536961538-ORNL_DAAC',
            'C179126725-ORNL_DAAC',
            'C179003380-ORNL_DAAC',
            'C179130805-ORNL_DAAC',
            'C179003657-ORNL_DAAC',
            'C1227811476-ORNL_DAAC',
            'C179130785-ORNL_DAAC'], result, "list matches")

    @patch('urllib.request.urlopen')
    def test_compound_search_gran(self, urlopen_mock):
        """
        Assuming that _collection_samples works and CMR work, test _granule_samples.
        Do this By hard coding the granule search and making sure that the remaining
        code correctly returns the granule information.
        """
        # Setup
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/cmr/search/combo_gran_result.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)

        # Inputs
        found_collections = ['C179003030-ORNL_DAAC',
            'C179002914-ORNL_DAAC',
            'C1000000000-ORNL_DAAC',
            'C1536961538-ORNL_DAAC',
            'C179126725-ORNL_DAAC',
            'C179003380-ORNL_DAAC',
            'C179130805-ORNL_DAAC',
            'C179003657-ORNL_DAAC',
            'C1227811476-ORNL_DAAC',
            'C179130785-ORNL_DAAC']
        filters=[gran.granule_core_fields, gran.drop_fields('GranuleUR'),
                gran.drop_fields('revision-id'),
                gran.drop_fields('native-id')]
        limit = 1
        config = {}

        # Run test
        found_granules = gran._granule_samples(found_collections, filters, limit, config)
        expected = [{'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'}]

        self.assertEqual(expected, found_granules, "Compound Search - Granual Compound")

    @patch('cmr.search.granule._collection_samples')
    @patch('urllib.request.urlopen')
    def test_compound_search(self, urlopen_mock, coll_mock):
        """
        Do a full test of the compound search, assuming that the component pieces
        work. Assume the response of the collection samples and hard code the CMR
        response for the granule search.
        """
        coll_mock.return_value = ['C179003030-ORNL_DAAC',
            'C179002914-ORNL_DAAC',
            'C1000000000-ORNL_DAAC',
            'C1536961538-ORNL_DAAC',
            'C179126725-ORNL_DAAC',
            'C179003380-ORNL_DAAC',
            'C179130805-ORNL_DAAC',
            'C179003657-ORNL_DAAC',
            'C1227811476-ORNL_DAAC',
            'C179130785-ORNL_DAAC']
        # Setup
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/cmr/search/combo_gran_result.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)

        collection_query = {'provider':'GHRC_CLOUD'}
        filters=[gran.granule_core_fields, gran.drop_fields('GranuleUR'),
                gran.drop_fields('revision-id'),
                gran.drop_fields('native-id')]

        # cut down the function parameters to assume all the parts that will not change
        runner = partial(gran.sample_by_collections, collection_query, filters=filters)

        # pylint: disable=C0301 # lambda must be on one line
        tester = lambda expected, limit, msg : self.assertEqual(expected, runner(limits=limit), msg)

        expected = [{'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'},
            {'concept-id': 'G1527288030-SEDAC'}]

        tester(expected, 10, "at most 10, default collection, using int")
        tester(expected, [10, 1], "at most 10, one collection, array")
        tester(expected[:5], {"granule": 5, "collection": 1}, "at most five, using dictionary")
        tester(expected, {"granule": 1, "collection": None}, "defaulting with dictionary")
