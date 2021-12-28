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
import os
from unittest.mock import Mock
from unittest.mock import patch
import unittest
import urllib.error as urlerr
import test.cmr as tutil
import cmr.util.common as common
import cmr.search.common as scom

# ******************************************************************************

def valid_cmr_response(file, status=200, headers=()):
    """return a valid login response"""
    json_response = common.read_file(file)
    return tutil.MockResponse(json_response, status=status, headers=headers)

class TestSearch(unittest.TestCase):
    """Test suit for Search API"""

    # **********************************************************************
    # Tests

    def test_meta_fields(self):
        """ Test that the meta fields are returned """
        test = lambda exp, given, msg : self.assertEqual(exp, scom.meta_fields(given), msg)
        test({}, {}, "empty")
        test({'key':'value'}, {'key':'value'}, "unrelated")
        test('meta-value', {'meta':'meta-value'}, "found a meta")

    def test_umm_fields(self):
        """ Test that the UMM fields are returned """
        test = lambda exp, given, msg : self.assertEqual(exp, scom.umm_fields(given), msg)
        test({}, {}, "empty")
        test({'key':'value'}, {'key':'value'}, "unrelated")
        test('umm-value', {'umm':'umm-value'}, "found a umm")

    def test_concept_id_fields(self):
        """ Test that the concept id fields are returned """
        test = lambda exp, given, msg : self.assertEqual(exp, scom.concept_id_fields(given), msg)
        test({}, {}, "empty")
        test({'key':'value'}, {'key':'value'}, "unrelated")
        test({'concept-id':'C123'}, {'meta':{'concept-id':'C123'}}, "found a concept-id in meta")
        test({'concept-id':'C123'}, {'concept-id':'C123'}, "found a concept-id")

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

    def test__error_object(self):
        """ Test that the Error Object is constructed correctly """
        err = lambda code, msg : {'errors': [msg], 'code':code, 'reason':msg}
        # pylint: disable=C0301 # lambda lines can not be shorter
        test = lambda code, emsg, msg : self.assertEqual(err(code, emsg), scom._error_object(code, emsg), msg)
        test(None, None, "nones")
        test(200, "OK", "200 msg")
        test(500, "Server Error", "500 error")

    def test_create_state(self):
        """Test the function which generates a page state"""
        base_state = scom.create_page_state()
        self.assertEqual(10, base_state['page_size'])
        self.assertEqual(1, base_state['page_num'])
        self.assertEqual(0, base_state['took'])
        self.assertEqual(10, base_state['limit'])

        limit_state = scom.create_page_state(limit=None)
        self.assertEqual(10, limit_state['page_size'])
        self.assertEqual(10, limit_state['limit'])

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
        basic_expected = {'Client-Id': 'python_cmr_lib', 'User-Agent': 'python_cmr_lib'}
        basic_result = scom._standard_headers_from_config({'a':1})
        self.assertEqual(basic_expected, basic_result)

        config = {'cmr-token': 'a-cmr-token',
            'X-Request-Id': '0123-45-6789',
            'Client-Id': 'fancy-client',
            'Not-A-Header': 'do not include me'}
        defined_expected = {'Echo-Token': 'a-cmr-token',
            'X-Request-Id': '0123-45-6789',
            'User-Agent': 'python_cmr_lib',
            'Client-Id': 'fancy-client'}
        defined_result = scom._standard_headers_from_config(config)
        self.assertEqual(defined_expected, defined_result)

        config = {'cmr-token': 'a-cmr-token',
            'Not-A-Header': 'do not include me'}
        token_expected = {'Echo-Token': 'a-cmr-token',
            'User-Agent': 'python_cmr_lib',
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
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/cmr/common/scroll_good.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, 204)
        result = scom.clear_scroll('-1')
        self.assertFalse('errors' in result)

        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/cmr/common/scroll_bad.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, 404)
        result = scom.clear_scroll('0')
        self.assertTrue('errors' in result)

    @patch('urllib.request.urlopen')
    def test__make_search_request(self, urlopen_mock):
        """
        Test the inner function which performs the first half of a search
        """
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/cmr/common/scroll_good.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, 204)
        page_state = scom.create_page_state()
        page_state['CMR-Scroll-Id'] = 'abcd'
        response = scom._make_search_request('search', {'keyword':'water'},
            page_state, {'env':'sit'})
        self.assertEqual({'http-headers': {}}, response,
            'test that the scroll id code gets touched')

    @patch('urllib.request.urlopen')
    @patch('cmr.search.common.clear_scroll')
    def test_search_by_page(self, clr_scroll_mock, urlopen_mock):
        """
        Test the inner function which performs the first half of a search
        """
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/cmr/search/ten_results_from_ghrc.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, 200)
        query = {'keyword':'water'}
        response = scom.search_by_page('collections', query)
        self.assertEqual(10, len(response), 'assumed page_state')

        # page state uses scroll
        page_state = scom.create_page_state(limit=4000)
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, 200,
            [('CMR-Scroll-Id','si-01')])
        page_state['CMR-Scroll-Id'] = 'abcd'
        response = scom.search_by_page('collections', query, page_state=page_state)
        self.assertEqual(20, len(response), 'assumed page_state')

        # error processing 1
        urlopen_mock.return_value = tutil.MockResponse("I'm a tea pot", 418)
        response = scom.search_by_page('collections', query, config={'debug':True})
        expected = {'errors': ['unknown response: I\'m a tea pot'],
            'code': 0,
            'reason': 'unknown response: I\'m a tea pot'}
        self.assertEqual(expected, response, "exeption")

        # error processing 2
        urlopen_mock.return_value = valid_cmr_response('{"errors":["Error"]}', 500)
        urlopen_mock.side_effect = urlerr.HTTPError(Mock(status=500), "500",
            "Server Error", None, None)
        response = scom.search_by_page('collections', query)
        expected = {'code': '500', 'reason': 'Server Error', 'errors': ['Server Error']}
        self.assertEqual(expected, response, "exeption")

        # bad clear response is logged
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/cmr/search/ten_results_from_ghrc.json')
        clr_scroll_mock.return_value = {'errors': ['bad scroll id']}
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, 200)
        urlopen_mock.side_effect = None
        response = scom.search_by_page('collections', query, page_state=page_state)
        self.assertEqual(10, len(response), "bad scroll id")

       # takes to long
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/cmr/search/ten_results_from_ghrc.json')
        page_state['took'] = 300001
        page_state['page_size'] = 1
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, 200)
        response = scom.search_by_page('collections', query, page_state=page_state)
        self.assertEqual(10, len(response), "bad scroll id")

    @patch('urllib.request.urlopen')
    def test_experimental_search(self, urlopen_mock):
        """
        def search(query=None, filters=None, limit=None, options=None):
        """
        # Setup
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/cmr/search/ten_results_from_ghrc.json')

        # Basic
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, 200)
        generator = scom.experimental_search_by_page_generator('collections',
            {'provider':'SEDAC'})
        for item in generator:
            self.assertEqual("ORNL_DAAC", item['meta']['provider-id'], 'basic test')

        # page state uses scroll
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, 200,
            [('CMR-Scroll-Id','abcd')])
        page_state = scom.create_page_state(limit=4000)
        page_state['CMR-Scroll-Id'] = 'abcd'
        generator = scom.experimental_search_by_page_generator('collections',
            {'provider':'SEDAC'}, page_state=page_state)
        for item in generator:
            self.assertEqual("ORNL_DAAC", item['meta']['provider-id'], 'trigger scrloll id check')

        # error processing writes to log
        urlopen_mock.side_effect = urlerr.HTTPError(Mock(status=500), "500",
            "Server Error", None, None)
        generator = None
        try:
            with self.assertLogs(scom.logger, level='ERROR') as test_log:
                try:
                    end_point = 'collections'
                    query = {'provider':'ORNL_DAAC'}
                    generator = scom.experimental_search_by_page_generator(end_point, query)
                    _ = next(generator) #consume generator to force action
                except StopIteration:
                    pass
                    #self.assertTrue(True, "generator should be empty")
                self.assertEqual(test_log.output,
                    ["ERROR:cmr.search.common:Error in generator: Server Error."],
                    "logs not matching")
        except AssertionError:
            self.fail('no log entry')

    @patch('webbrowser.open')
    def test_open_api(self, webopener):
        """ Test the function of the open_api without actually opening it """
        webopener.return_value = "ok"
        self.assertEqual(None, scom.open_api('section'))

    # need to test search_by_page
