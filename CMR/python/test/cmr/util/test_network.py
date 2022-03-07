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

from unittest.mock import Mock
from unittest.mock import patch
import unittest

import urllib.error as urlerr

import test.cmr as tutil

from cmr.util import common
import cmr.util.network as net

# ******************************************************************************

def valid_cmr_response(file, status=200, headers=() ):
    """return a valid login response"""
    json_response = common.read_file(file)
    return tutil.MockResponse(json_response, status=status, headers=headers)

class TestSearch(unittest.TestCase):
    """Test suit for Search API"""

    # **********************************************************************
    # Util methods

    # **********************************************************************
    # Tests

    def test_local_ip(self):
        """ This is a stub function, testing it should be pretty easy. """
        self.assertEqual('127.0.0.1', net.get_local_ip(), "local IP failed")

    def test_value_to_param(self):
        """ Test that a value can be converted to a URL parameter """
        # pylint: disable=C0301 # lambda lines can be shorter
        test = lambda expected, key, value, msg : self.assertEqual(expected, net.value_to_param(key, value), msg)
        test("key=value", "key", "value", "Basic")
        test("key=", "key", "", "Missing Value")
        test("=value", "", "value", "Missing Key")
        test("a%20key=value", "a key", "value", "Key with space")
        test("key=a%20value", "key", "a value", "Value with space")
        test("key%3D=%3Dvalue", "key=", "=value", "Using equal signs")

    def test_expand_parameter_to_parameters(self):
        """ Test the function that converts a key value pair into a list """
        self.assertEqual(['='], net.expand_parameter_to_parameters('', ''))
        self.assertEqual(['key=v1'], net.expand_parameter_to_parameters('key', 'v1'))
        self.assertEqual(['key=v%201'], net.expand_parameter_to_parameters('key', 'v 1'))

        expected = ['key=v1', 'key=v2']
        actual = net.expand_parameter_to_parameters('key', ['v1','v2'])
        self.assertEqual(expected, actual)

    def test_expand_query_to_parameters(self):
        """ Test the function that expands dictionaries into URL queries """
        self.assertEqual('', net.expand_query_to_parameters({}))
        self.assertEqual('key1=v1', net.expand_query_to_parameters({'key1':'v1'}))

        expected1 = 'key1=v1&key2=v2'
        expected2 = 'key2=v2&key1=v1'
        actual = net.expand_query_to_parameters({'key1':'v1', 'key2':'v2'})
        self.assertTrue(actual in [expected1,expected2])

    def test_apply_headers_to_request(self):
        """test that the function will add headers to an object that has add_header()"""
        header = {"agent" : "x", 'encoding': "xml"}

        class Req():
            """ mock the request object """
            def __init__ (self):
                self.headers = {}
            def add_header(self, key, value):
                """ make sure that code here can manipulate headers """
                self.headers[key] = value
            def get_header(self, key, default=None):
                """
                pylint complained that this object had "too-feew-public-methods
                so this function is now included
                """
                if key in self.headers:
                    return self.headers[key]
                return default
        req = Req()
        net.apply_headers_to_request(req, header)
        self.assertEqual("x", req.headers['agent'], 'agent was added')
        self.assertEqual("xml", req.headers['encoding'], 'encoding was added')

    def test_transform_results(self):
        """
        Test the function that converts CMR URL parameter queries which
        contain multiple values into a dictionary that contains lists
        """
        self.assertEqual({}, net.transform_results({}, None))
        self.assertEqual({}, net.transform_results({}, {}))

        data = [{'key1':'v1'},{'key1':'v2'}]
        result = net.transform_results(data, ['key1'])
        expected = {'key1': ['v1', 'v2']}
        self.assertEqual(expected, result)

        data = [{'key1':'v1'},{'key1':'v2'},{'key2':'v3'}]
        result = net.transform_results(data, ['key1'])
        expected = {'key1': ['v1', 'v2']}
        self.assertEqual(expected, result)

        data = [{'key1':'v1'},{'key1':'v2'},{'key2':'v3'}]
        result = net.transform_results(data, ['key1','key2'])
        expected = {'key1': ['v1', 'v2'], 'key2': ['v3']}
        self.assertEqual(expected, result)

    def test_config_to_header(self):
        """
        Test the helper function which converts values in the config dictionary
        to the header dictionary
        """
        # pylint: disable=C0301 # lambda lines can be shorter
        test = lambda exp, opt, src, head, dest=None, defa=None : self.assertEqual(exp, net.config_to_header(opt, src, head, dest, defa))

        test(None, None, None, None)
        test({}, {}, 'user-setting', {})
        test({}, {'user-setting':None}, 'user-setting', {})

        opt = {'user-setting':'Value-One','other':'Value-Two'}
        test({'user-setting':'Value-One'}, opt, 'user-setting', {})

        expected = {'user-setting':'Value-One','existing':'Value-3'}
        src = {'user-setting':'Value-One','other':'Value-Two'}
        test(expected, src, 'user-setting', {'existing':'Value-3'})

        expected = {'renamed':'V-2'}
        src = {'user-setting':'V-1','change-me':'V-2', 'other':'V-3'}
        test(expected, src, 'change-me', {}, 'renamed')

        expected = {'Default-Value':'Always'}
        test(expected, {}, 'Not-Given', {}, 'Default-Value', 'Always')

    @patch('urllib.request.urlopen')
    def test_post(self, urlopen_mock):
        """ Test the post method, POST a network resource """
        # Setup
        recorded_data_file = tutil.resolve_full_path('../data/cmr/search/one_cmr_result.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)

        data = net.post("http://cmr.earthdata.nasa.gov/search", {})
        self.assertEqual(276, (data['hits']))

        data = net.post("http://cmr.earthdata.nasa.gov/search", {}, accept='application/xml')
        self.assertEqual(276, (data['hits']))

        data = net.post("http://cmr.earthdata.nasa.gov/search", {}, headers={'platforms':'SMAP'})
        self.assertEqual(276, (data['hits']))

        # test that a 200 with headers will be logged
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, 200,
            [('head-a', 'value-a')])
        try:
            net.logger.setLevel('DEBUG')
            with self.assertLogs(net.logger, level='DEBUG') as test_log:
                data = net.post("http://cmr.earthdata.nasa.gov/search", {})
                self.assertEqual({"head-a": "value-a"}, data['http-headers'],
                    "headers do not match")

            self.assertEqual(test_log.output,
                ['DEBUG:cmr.util.network: Headers->CMR= None',
                    "DEBUG:cmr.util.network: POST Data= b''",
                    "DEBUG:cmr.util.network: CMR->Headers = {'head-a': 'value-a'}"],
                "log does not match")
        except AssertionError:
            self.fail('no log entry')
        net.logger.setLevel('ERROR')

        # test that a 204 can be processed
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, 204,
            [('head-a', 'value-a')])
        data = net.post("http://cmr.earthdata.nasa.gov/search", {})
        self.assertEqual({'http-headers':{"head-a": "value-a"}}, data)

        # test an error
        urlopen_mock.side_effect = urlerr.HTTPError(Mock(status=500), "500",
            "Unprocessable Entity", None, None)
        data = net.post("http://cmr.earthdata.nasa.gov/search/fake", {})
        expected = {'code': '500',
            'reason': 'Unprocessable Entity',
            'errors': ['Unprocessable Entity']}
        self.assertEqual(expected, data)

    @patch('urllib.request.urlopen')
    def test_get(self, urlopen_mock):
        """ Test the get method, get a network resource """
        # Setup
        recorded_data_file = tutil.resolve_full_path('../data/cmr/search/one_cmr_result.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)

        data = net.get("http://cmr.earthdata.nasa.gov/search")
        self.assertEqual(276, (data['hits']), "only required parameters")

        data = net.get("http://cmr.earthdata.nasa.gov/search", accept='application/xml')
        self.assertEqual(276, (data['hits']), "with an accept")

        data = net.get("http://cmr.earthdata.nasa.gov/search", headers={'platforms':'SMAP'})
        self.assertEqual(276, (data['hits']), "with a header")

        # test that a 200 can be processed with headers by writing to log
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, 200, [('key', 'value')])
        try:
            net.logger.setLevel('DEBUG')
            with self.assertLogs(net.logger, level='DEBUG') as test_log:
                data = net.get("http://cmr.earthdata.nasa.gov/search")
            self.assertEqual(test_log.output,
                ['DEBUG:cmr.util.network: Headers->CMR= None',
                "DEBUG:cmr.util.network: CMR->Headers = {'key': 'value'}"])
        except AssertionError:
            self.fail("no log entry")
        net.logger.setLevel('ERROR')

        # test that a 204 can be processed
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, 204, [('key', 'value')])
        data = net.get("http://cmr.earthdata.nasa.gov/search")
        self.assertEqual({'http-headers':{'key':'value'}}, data, "a 204 response")

        # standard tea pot test : error handling
        urlopen_mock.return_value = tutil.MockResponse("I'm a tea pot", 416, [('key', 'value')])
        data = net.get("http://cmr.earthdata.nasa.gov/search")
        self.assertEqual("I'm a tea pot", data, "a 416 response")

        # exception handling
        urlopen_mock.side_effect = urlerr.HTTPError(Mock(status=500), "500",
            "Server Error", None, None)
        data = net.get("http://cmr.earthdata.nasa.gov/search")
        expected = {'code': '500', 'reason': 'Server Error', 'errors': ['Server Error']}
        self.assertEqual(expected, data, "exception was not caught")

        # test an error
        urlopen_mock.side_effect = urlerr.HTTPError(Mock(status=500), "500",
            "Unprocessable Entity", None, None)
        data = net.get("http://cmr.earthdata.nasa.gov/search/fake")
        expected = {'code': '500',
            'reason': 'Unprocessable Entity',
            'errors': ['Unprocessable Entity']}
        self.assertEqual(expected, data, "an exeption")
        urlopen_mock.side_effect = None

        # test list response such as the provider list from ingest
        recorded_data_file = tutil.resolve_full_path('../data/cmr/ingest/providers.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)
        data = net.get("http://cmr.earthdata.nasa.gov/ingest/providers?pretty=true")
        self.assertEqual(110, len(data['items']))
