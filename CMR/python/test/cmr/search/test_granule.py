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
from unittest.mock import patch
import unittest

import test.cmr as tutil

import cmr.util.common as common
import cmr.search.granule as gran

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

    @patch('urllib.request.urlopen')
    def test_search(self, urlopen_mock):
        """
        def search(query=None, filters=None, limit=None, options=None):
        """
        # Setup
        urlopen_mock.return_value = valid_cmr_response(
            'test/data/cmr/search/one_granule_cmr_result.json')

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

    def test_apply_filter(self):
        """Test that apply filters function can be used to strip items out of the data"""
        data = [{'a':'11', 'b':'21', 'c':'31'}, {'a':'12', 'b':'22', 'c':'32'}]
        result = gran.apply_filters([gran.drop_fields('a'), gran.drop_fields('b')], data)
        expected = [{'c': '31'}, {'c': '32'}]
        self.assertEqual (expected, result)

    def test_help_full(self):
        """Test the built in help"""
        result_full = gran.print_help()
        self.assertTrue (-1<result_full.find("granule_core_fields"))
        self.assertTrue (-1<result_full.find("search():"))

    def test_help_less(self):
        """Test the built in help for filtering"""
        result_less = gran.print_help("_fields")
        self.assertTrue (-1<result_less.find("granule_core_fields"))
        self.assertFalse (-1<result_less.find("search():"))
