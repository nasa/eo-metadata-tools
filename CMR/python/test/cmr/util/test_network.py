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
#from unittest.mock import patch
import unittest

#import test.cmr as tutil

#import cmr.auth.token as token
#import cmr.auth.login as login
#import cmr.util.common as common
import cmr.util.network as net

# ******************************************************************************

class TestSearch(unittest.TestCase):
    """Test suit for Search API"""

    # **********************************************************************
    # Util methods

    # **********************************************************************
    # Tests

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
