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
Test cases for the cmr.search.providers module
Author: thomas.a.cherry@nasa.gov - NASA
Created: 2022-03-09
"""

from unittest.mock import patch
import unittest

import test.cmr as tutil

from cmr.util import common
import cmr.search.providers as prov

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
    def test_search(self, urlopen_mock):
        """ Check that a good query will result in finding providers """
        # Setup
        recorded_file = tutil.resolve_full_path('../data/cmr/search/providers_result.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_file)

        data1 = prov.search()
        data2 = prov.search(config={'env':'sit'})

        for data in [data1, data2]:
            self.assertNotIn('errors', data, "errors in data")
            self.assertEqual(143, len(data), "record count match")
            self.assertEqual('ORNL_DAAC', data[0].get('short-name'))
            self.assertEqual('GEOSS', data[len(data)-1].get('consortiums'))

    @patch('urllib.request.urlopen')
    def test_search_by_id(self, urlopen_mock):
        """
        Check that a good query with filtering will result in finding a subset
        of providers
        """
        # Setup
        recorded_file = tutil.resolve_full_path('../data/cmr/search/providers_result.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_file)

        data1 = prov.search_by_id(None, config={'env':'sit'})
        data2 = prov.search_by_id('', config={'env':'sit'})
        for data in [data1,data2]:
            self.assertNotIn('errors', data, "errors in data")
            self.assertEqual(143, len(data), "record count match")
            self.assertEqual('ORNL_DAAC', data[0].get('short-name'))
            self.assertEqual('GEOSS', data[len(data)-1].get('consortiums'))

        data1 = prov.search_by_id('.*NOAA.*', config={'env':'sit'})
        data2 = prov.search_by_id('.*noaa.*', config={'env':'sit'})
        for data in [data1,data2]:
            self.assertNotIn('errors', data, "errors in data")
            self.assertEqual(5, len(data), "record count match")
            self.assertEqual('NOAA_TEST', data[0].get('short-name'))
            self.assertEqual('NOAA_NCEI', data[len(data)-1].get('short-name'))

        bad_data = prov.search_by_id('*noaa*', config={'env':'sit'})
        self.assertIn('errors', bad_data, 'error on bad query')
        self.assertEqual(['Regular Expression is invalid and could not compile'],
            bad_data.get('errors'), 'Bad Search')

    @patch('urllib.request.urlopen')
    def test_search_bad(self, urlopen_mock):
        """
        There is no documented error from this interface, however the code will
        respond if one is added.
        """
        # Setup
        recorded_file = tutil.resolve_full_path('../data/cmr/search/providers_bad_result.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_file)

        data1 = prov.search()
        data2 = prov.search(config={'env':'sit'})
        data3 = prov.search_by_id('YRUAB')

        for data in [data1, data2, data3]:
            self.assertIn('errors', data, "errors in data")
            self.assertEqual(['An unexpected error was reported'], data.get('errors'),
                "error contains one message")

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
            prov.open_api('#some-page-tag', "not supported")
            prov.set_logging_to()

        # most general test that could be made
        # pylint: disable=W0703 # exception is the best way to look for the unexpected
        try:
            prov.open_api()
            prov.set_logging_to(0)
        except Exception:
            self.fail("un expected error")

    def test_help_full(self):
        """Test the built in help"""
        result_full = prov.help_text()
        self.assertTrue (-1<result_full.find("search"))
        self.assertTrue (-1<result_full.find("search_by_id"))
        self.assertTrue (-1<result_full.find("set_logging_to"))

    def test_help_less(self):
        """Test the built in help for filtering"""
        result_less = prov.help_text("search")
        self.assertTrue (-1<result_less.find("search"))
        self.assertTrue (-1<result_less.find("search_by_id"))
        self.assertFalse (-1<result_less.find("set_logging_to"))
