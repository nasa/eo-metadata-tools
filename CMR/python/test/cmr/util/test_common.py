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
        self.assertEqual([3, 4], com.conj(None, [3, 4]))
        self.assertEqual([1, 2, 3, 4], com.conj([1, 2], [3, 4]))
        self.assertEqual((4, 3, 1, 2), com.conj((1, 2), (3, 4)))
        self.assertEqual({'a': 'A', 'b': 'B'}, com.conj({'a':'A'}, {'b':'B'}))
