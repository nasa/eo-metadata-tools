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

import os
import uuid

import cmr.util.common as com

# ******************************************************************************

class TestSearch(unittest.TestCase):
    """Test suit for Search API"""

    # **********************************************************************
    # Util methods

    # **********************************************************************
    # Tests

    def test_conj(self):
        """Test the conj function"""
        self.assertEqual([3, 4], com.conj(None, [3, 4]), 'src was None')
        self.assertEqual([1, 2, 3, 4], com.conj([1, 2], [3, 4]), 'good src, lists')
        self.assertEqual((4, 3, 1, 2), com.conj((1, 2), (3, 4)), 'good src, tuples')
        self.assertEqual({'a': 'A', 'b': 'B'}, com.conj({'a':'A'}, {'b':'B'}), 'good src, dict')

    def test_always(self):
        """Test the always function"""
        self.assertEqual({}, com.always("wrong type"), 'wrong thing')
        self.assertEqual({}, com.always([]), 'wrong type')
        self.assertEqual({}, com.always({}), 'same type')
        self.assertEqual({'a':'b'}, com.always({'a':'b'}), 'populated dict, assumed')
        self.assertEqual({'a':'b'}, com.always({'a':'b'}, otype=dict), 'populated dict')
        self.assertEqual(['a', 'b'], com.always(['a','b'], otype=list), 'populated list')
        self.assertEqual((1,2,3), com.always((1,2,3), otype=tuple), 'populated tuple')
        self.assertEqual((1,2,3), com.always((1,2,3), tuple), 'populated tuple, positional')

        # None use cases
        self.assertEqual({}, com.always(None), 'assumed, none, dict')
        self.assertEqual({}, com.always(None, otype=dict), 'None, dict')
        self.assertEqual([], com.always(None, otype=list), 'None, list')
        self.assertEqual((), com.always(None, otype=tuple), 'None, tuple')
        self.assertEqual((), com.always(None, tuple), 'None, tuple, positional')

    def test_drop_key_safely(self):
        """Test that values can be dropped safely"""
        # pylint: disable=C0301 # lambdas must be on one line
        tester = lambda expected, src, key, msg : self.assertEqual(expected, com.drop_key_safely(src, key), msg)
        tester({}, {}, "Not existing", "Empty dictionary")
        tester({"key":"value"}, {"key": "value"}, "not found", "wrong key, no drop")
        tester({}, {"key":"value"}, "key", "drop found key")

    def test_write_read_round_trip(self):
        """
        Test the read and write functions by doing a full round trip test. Save
        some text to a temp file, then read it back, testing both functions at once
        """
        path = "/tmp/" + str(uuid.uuid4())
        expected = str(uuid.uuid4())
        com.write_file(path, expected)
        actual = com.read_file(path)
        os.remove(path) # cleanup now
        self.assertEqual(expected, actual, "Write-Read round trip")

    def test_execute_command(self):
        """Execute will run any command, test that it behaves as expected"""
        # pylint: disable=C0301 # lambdas must be on one line
        tester = lambda expected, given, msg : self.assertEqual(expected, com.execute_command(given), msg)
        tester("", "true", "Test a single command response")
        tester("_result_", ["printf", '_%s_', 'result'], "Test a command with properties")

    @patch('cmr.util.common.execute_command')
    def test_security_call(self, execute_command_mock):
        """
        test that the code will call an external command and respond as expected
        """
        execute_command_mock.return_value = " response info "
        self.assertEqual("response info", com.call_security("account", "service"), "Good response")

        execute_command_mock.return_value = None
        try:
            com.call_security("account", "service")
        except TypeError as err:
            self.assertEqual('account not found in keychain', str(err), "Bad response")

    def test_help_format_lambda(self):
        """Test that the lambda function performs as expected"""
        cmd = com.help_format_lambda()
        self.assertTrue("str(object='') -> str" in cmd("str", ""))

    def test_mask_string(self):
        """Test that the mask_diictionary function will clean out sensitive info"""
        # pylint: disable=C0301 # lambdas must be on one line
        tester = lambda expected, given, msg : self.assertEqual(expected, com.mask_string(given), msg)

        tester("", None, "None sent")
        tester("", "", "No Letters")
        tester("0", "0", "One letter")
        tester("01", "01", "Two Letters")
        tester("0*2", "012", "Three Letters")
        tester('EDL-U123********34567890', 'EDL-U12345678901234567890', "Real example")

    def test_mask_dictionary(self):
        """Test that the mask_diictionary function will clean out sensitive info"""
        data = {'ignore': 'this',
            'token': '012345687', 'cmr-token': 'EDL-U12345678901234567890'}
        expected1 = {'ignore': 'this',
            'token': '012345687', 'cmr-token': 'EDL-U123********34567890'}
        expected2 = {'ignore': 'this',
            'token': '012***687', 'cmr-token': 'EDL-U12345678901234567890'}
        expected3 = {'ignore': 'this',
            'token': '012345687', 'cmr-token': 'EDL-U12345678901234567890'}
        expected4 = {'ignore': 'this',
            'token': '012***687', 'cmr-token': 'EDL-U123********34567890'}

        self.assertEqual(expected1, com.mask_dictionary(data, 'cmr-token'))
        self.assertEqual(expected1, com.mask_dictionary(data, ['cmr-token']))

        self.assertEqual(expected2, com.mask_dictionary(data, 'token'))
        self.assertEqual(expected2, com.mask_dictionary(data, ['token']))

        self.assertEqual(expected3, com.mask_dictionary(data, 'cmr'))
        self.assertEqual(expected3, com.mask_dictionary(data, ['cmr']))

        self.assertEqual(expected4, com.mask_dictionary(data, ['token', 'cmr-token']))

        self.assertEqual(data, com.mask_dictionary(data, ''))
        self.assertEqual(data, com.mask_dictionary(data, []))
