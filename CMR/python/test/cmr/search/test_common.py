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
Created: 2020-11-30
"""

from unittest.mock import patch
import unittest
import test.cmr as tutil
import cmr.util.common as common
import cmr.search.common as scom

# ******************************************************************************

def valid_cmr_response(file, status=200):
    """return a valid login response"""
    json_response = common.read_file(file)
    return tutil.MockResponse(json_response, status=status)

class TestSearch(unittest.TestCase):
    """Test suit for Search API"""

    # **********************************************************************
    # Tests

    # pylint: disable=W0212
    def test_next_state(self):
        """Check that the sort by attribute is added correctly"""
        #setup
        orig_state = scom.create_page_state()
        # try once
        next_state = scom._next_page_state(orig_state, 10)
        self.assertEqual(10, next_state['took'])
        self.assertEqual(2, next_state['page_num'])
        # try again
        final_state = scom._next_page_state(next_state, 10)
        self.assertEqual(20, final_state['took'])
        self.assertEqual(3, final_state['page_num'])

    def test_create_state(self):
        """Test the function which generates a page state"""
        base_state = scom.create_page_state()
        self.assertEqual(10, base_state['page_size'])
        self.assertEqual(1, base_state['page_num'])
        self.assertEqual(0, base_state['took'])
        self.assertEqual(10, base_state['limit'])

        limit_state = scom.create_page_state(limit=1000)
        self.assertEqual(1000, limit_state['page_size'])
        self.assertEqual(1000, limit_state['limit'])

        limit_priority_state = scom.create_page_state(page_size=1500, limit=1200)
        self.assertEqual(1200, limit_priority_state['page_size'])
        self.assertEqual(1200, limit_priority_state['limit'])

        mixed_state = scom.create_page_state(page_size=1200, limit=1500)
        self.assertEqual(1500, mixed_state['page_size'])
        self.assertEqual(1500, mixed_state['limit'])

        high_state = scom.create_page_state(page_size=1000, limit=4000)
        self.assertEqual(2000, high_state['page_size'])
        self.assertEqual(4000, high_state['limit'])

        high_state = scom.create_page_state(limit=2048)
        self.assertEqual(683, high_state['page_size'])

    # pylint: disable=W0212
    def test_continue_download(self):
        """Test the function that checks if enough records have been downloaded"""
        #limit to 10, 10 per page, first page
        page_state = scom.create_page_state()
        self.assertFalse(scom._continue_download(page_state))

        #limit to 1000, 1000 per page, first page
        page_state = scom.create_page_state(limit=1000)
        self.assertFalse(scom._continue_download(page_state))

        #limit to 4000, 2000 per page, first page
        page_state = scom.create_page_state(limit=4000)
        self.assertTrue(scom._continue_download(page_state))

        #limit to 1000, 2000 per page, second page
        page_state = scom.create_page_state(page_num=2, limit=4000)
        self.assertFalse(scom._continue_download(page_state))

        #limit to 1000, 683 per page, second page
        page_state = scom.create_page_state(page_num=1, limit=2048)
        self.assertTrue(scom._continue_download(page_state))

        #limit to 2048, 683 per page, second page
        page_state = scom.create_page_state(page_num=2, limit=2048)
        self.assertTrue(scom._continue_download(page_state))

        #limit to 2048, 683 per page, third page
        page_state = scom.create_page_state(page_num=3, limit=2048)
        self.assertFalse(scom._continue_download(page_state))

    # pylint: disable=W0212
    def test_standard_headers_from_config(self):
        """Test that standard headers can be setup"""
        basic_expected = {'Client-Id': 'python_cmr_lib'}
        basic_result = scom._standard_headers_from_config({'a':1})
        self.assertEqual(basic_expected, basic_result)

        config = {'cmr-token': 'a-cmr-token',
            'X-Request-Id': '0123-45-6789',
            'Client-Id': 'fancy-client',
            'Not-A-Header': 'do not include me'}
        defined_expected = {'Echo-Token': 'a-cmr-token',
            'X-Request-Id': '0123-45-6789',
            'Client-Id': 'fancy-client'}
        defined_result = scom._standard_headers_from_config(config)
        self.assertEqual(defined_expected, defined_result)

        config = {'cmr-token': 'a-cmr-token',
            'Not-A-Header': 'do not include me'}
        token_expected = {'Echo-Token': 'a-cmr-token',
            'Client-Id': 'python_cmr_lib'}
        token_result = scom._standard_headers_from_config(config)
        self.assertEqual(token_expected, token_result)

    # pylint: disable=W0212
    def test_cmr_query_url(self):
        """ Test that a CMR url can be built correctly"""
        page_state = scom.create_page_state()
        result = scom._cmr_query_url("search", {'provider':'p01'}, page_state,
            config={'env':'sit'})
        expected = 'https://cmr.sit.earthdata.nasa.gov/search/search?' \
            'page_size=10&provider=p01'
        self.assertEqual(expected, result)

        #now test for scrolling
        page_state = scom.create_page_state(limit=2048)

        result = scom._cmr_query_url("search", {'provider':'p01'}, page_state,
            config={'env':'sit'})
        expected = 'https://cmr.sit.earthdata.nasa.gov/search/search?' \
            'page_size=683&provider=p01&scroll=true'
        self.assertEqual(expected, result)

        #now test for scrolling
        result = scom._cmr_query_url("search", {'provider':'p01'}, page_state,
            config={'env':'sit'})
        expected = 'https://cmr.sit.earthdata.nasa.gov/search/search?' \
            'page_size=683&provider=p01&scroll=true'
        self.assertEqual(expected, result)

        result = scom._cmr_query_url("search", {'provider':'p01'}, page_state,
            config={'env':'sit.'})
        expected = 'https://cmr.sit.earthdata.nasa.gov/search/search?' \
            'page_size=683&provider=p01&scroll=true'
        self.assertEqual(expected, result)

        result = scom._cmr_query_url("search", {'provider':'p01'}, page_state,
            config={})
        expected = 'https://cmr.earthdata.nasa.gov/search/search?' \
            'page_size=683&provider=p01&scroll=true'
        self.assertEqual(expected, result)

        result = scom._cmr_query_url("search", {}, page_state, config={})
        expected = 'https://cmr.earthdata.nasa.gov/search/search?' \
            'page_size=683&scroll=true'
        self.assertEqual(expected, result)

    @patch('urllib.request.urlopen')
    def test_scroll(self, urlopen_mock):
        """ Test the scroll clear function to see if it returns an error or not"""
        recorded_data_file = 'test/data/cmr/common/scroll_good.json'
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, 204)
        result = scom.clear_scroll('-1')
        self.assertFalse('errors' in result)

        recorded_data_file = 'test/data/cmr/common/scroll_bad.json'
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, 404)
        result = scom.clear_scroll('0')
        self.assertTrue('errors' in result)
