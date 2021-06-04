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

    def test_mask_string(self):
        """Test that the mask_diictionary function will clean out sensitive info"""
        data = 'EDL-U12345678901234567890'
        expected1 = 'EDL-U123********34567890'
        self.assertEqual(expected1, com.mask_string(data))

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
