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
Date: 2020-10-15
Since: 0.0
"""

import os
import json
import subprocess
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch
import unittest

import test.cmr as util
import cmr.auth.token as token
import cmr.util.common as common

# ******************************************************************************

def valid_cmr_response(file, status=200):
    """return a valid login response"""
    json_response = common.read_file(file)
    return util.MockResponse(json_response, status=status)

class TestToken(unittest.TestCase):
    """ Test suit for cmr.auth.token """

    # **********************************************************************
    # Tests

    # pylint: disable=R0904 ; 27 tests is not unheard of
    def test_token_literal(self):
        """
        Test the literal token manager function which returns a token lambda
        """
        expected = "some-token-value"

        # returns a valid token
        manager = token.token_literal(expected)
        actual = manager({})
        self.assertEqual(expected, actual)
        actual = manager(None)
        self.assertEqual(expected, actual)

        # returns no token
        manager = token.token_literal(None)
        actual = manager({})
        self.assertEqual(None, actual)

    def test_token_config(self):
        """ Test the manager which pulls token from the configuration object """
        expected = "some-token-value"

        actual = token.token_config(None)
        self.assertEqual(None, actual)

        actual = token.token_config({})
        self.assertEqual(None, actual)

        actual = token.token_config({'cmr.token.value':expected})
        self.assertEqual(expected, actual)

    def test_token_file(self):
        """
        Test a valid login using the password file lambda with caching on. This
        will require that the test be able to write to a temp directory
        """
        #setup
        token_file = "/tmp/__test_token_file__.txt"
        util.delete_file(token_file)
        expected_token = "file-token"
        common.write_file(token_file, expected_token)

        #tests
        options = {'cmr.token.file': token_file}
        self.assertEqual (expected_token, token.token_file(options))

        actual = str(token.token(token.token_file, options))
        self.assertEqual (expected_token, actual)

        actual_token = common.read_file(token_file)
        self.assertEqual(expected_token, actual_token)

        #cleanup
        util.delete_file(token_file)

    @patch("cmr.util.common.call_security")
    def test_token_manager(self, security_mock):
        """ Test that the token manager can handle a bad Process Exception """
        security_mock.side_effect = subprocess.CalledProcessError(Mock(), "/usr/bin/fake-123")
        actual = token.token_manager({'token.manager.app':'/usr/bin/fake-123'})
        self.assertEqual(None, actual, "error recovery")

    def test_bearer(self):
        """Test a that a token can be returned as a Bearer token"""
        #setup
        token_file = "/tmp/__test_token_file__.txt"
        util.delete_file(token_file)
        expected_token = "file-token"
        expected_bearer = "Bearer " + expected_token
        common.write_file(token_file, expected_token)

        #tests
        options = {'cmr.token.file': token_file}
        actual = str(token.bearer(token.token_file, options))
        self.assertEqual (expected_bearer, actual, "Token formated as Bearer")

        #cleanup
        util.delete_file(token_file)

    def test_use_bearer_token(self):
        """Test the function that handles all the work of tokens"""
        tokener = token.token_literal("test") #this always returns test as token
        # pylint: disable=C0301 # lambdas must be on one line
        tester = lambda expected, given, msg : self.assertEqual(expected, token.use_bearer_token(token_lambdas=tokener, config=given), msg)

        tester({"authorization":"Bearer test"}, None, "found from none")
        tester({"authorization":"Bearer test"}, {}, "found from nothing")
        tester({"authorization":"Bearer test"},
            {"authorization":"old value"},
            "replace")
        tester({"authorization":"Bearer test", "unrelated":"value"},
            {"authorization":"old value", "unrelated":"value"},
            "replace, ignoring others")

    # pylint: disable=W0212 ; test a private function
    def test__env_to_extention(self):
        """Check that the environment->extensions work as expected"""
        # pylint: disable=C0301 # lambdas must be on one line
        test = lambda expected, given, msg : self.assertEqual(expected, token._env_to_extention(given), msg)

        test("", None, "No dictionary given")
        test("", {}, "Empty dictionary")
        test("", {"env":None}, "Emtpy value")
        test("", {"env":""}, "Blank value")
        test("", {"env":"ops"}, "Ops specified")
        test("", {"env":"ops."}, "Ops with a dot specified")
        test("", {"env":"prod"}, "Production specified")
        test("", {"env":"production"}, "Production specified")
        test(".uat", {"env":"uat"}, "UAT specified")
        test(".sit", {"env":"sit"}, "SIT specified")
        test(".sit", {"env":"sit."}, "SIT with a dot specified")
        test(".future", {"env":"future"}, "Future envirnment")

    def test__env_to_edl_url(self):
        """
        Test that an EDL URL can be generated with a given endpoint and config
        """
        # pylint: disable=C0301 # lambdas must be on one line
        test = lambda expected, given, config, msg : self.assertEqual(expected, token._env_to_edl_url(given, config=config), msg)

        expected_token_ops = 'https://urs.earthdata.nasa.gov/api/users/token'
        expected_token_uat = 'https://uat.urs.earthdata.nasa.gov/api/users/token'
        expected_token_sit = 'https://sit.urs.earthdata.nasa.gov/api/users/token'

        test(expected_token_ops, 'token', None, "None test")
        test(expected_token_ops, 'token', {}, "Empty test")
        test(expected_token_ops, 'token', {'env': None}, "env empty test")
        test(expected_token_ops, 'token', {'env':'ops'}, "OPS test")
        test(expected_token_uat, 'token', {'env':'uat'}, "UAT test")
        test(expected_token_sit, 'token', {'env':'sit'}, "SIT test")

    # pylint: disable=W0212 ; test a private function
    def test_token_file_env(self):
        """Test the function that returns the token file path"""
        # pylint: disable=C0301 # lambdas must be on one line
        test = lambda expected, config, msg: self.assertEqual(expected, token._token_file_path(config), msg)

        test("~/.cmr_token", None, "Not specified")
        test("~/.cmr_token", {"env" : None}, "None value")
        test("~/.cmr_token", {"env" : ""}, "Empty value")
        test("~/.cmr_token", {"env" : "OPS"}, "OPS specified")
        test("~/.cmr_token.uat", {"env" : "uat"}, "UAT specified")
        test("~/.cmr_token.uat", {"env" : "Uat"}, "UAT, mixed case, specified")
        test("~/.cmr_token.sit", {"env" : "sit"}, "SIT specified")

        test("/tmp/token", {"env": "sit", "cmr.token.file": "/tmp/token"}, "File specified")

    def test_token_file_ignoring_comments(self):
        """
        Test a valid login using the password file lambda. The file itself will
        contain comments to be ignored. This test will require that the test be
        able to write to a temp directory
        """
        #setup
        token_file = "/tmp/__test_token_file__.txt"
        util.delete_file(token_file)
        expected_token = "file-token"
        token_file_content = "#ignore this line\n" + expected_token
        common.write_file(token_file, token_file_content)

        #tests
        actual_token = common.read_file(token_file)
        self.assertEqual(token_file_content, actual_token)

        options = {'cmr.token.file': token_file}
        self.assertEqual (expected_token, token.token_file(options))

        actual = str(token.token(token.token_file, options))
        self.assertEqual (expected_token, actual)

        #cleanup
        util.delete_file(token_file)

    def test__base64_text(self):
        "Test that the base64 library encodes values as the code expects"
        # pylint: disable=C0301 # lambdas must be on one line
        test = lambda expected, given, msg : self.assertEqual(expected, token._base64_text(given), msg)

        test("", "", "Empty Test")
        test("RW5jb2RlIHRoaXMgbWVzc2FnZQ==", "Encode this message", "Value Test")
        test("dXNlcjpjb2Rl", "user:code", "Real World Test")

    def test__lambda_list_always(self):
        "Test the generation of a default lambda list "
        # pylint: disable=C0301 # lambdas must be on one line
        test = lambda expected, given, fallback, msg : self.assertEqual(expected, token._lamdba_list_always(given, fallback), msg)
        test([token.token_file, token.token_config], None, None, "None, with no fallback Test")
        test([], None, [], "None, with Empty fallback Test")
        test(['a'], 'a', None, "Not a list")
        test([], [], None, "Empty, with no fallback Test")
        test([], [], [], "Empty, with empty fallback Test")
        test([token.token_config], None, [token.token_config], "None, with fallback Test")
        test([token.token_config], [token.token_config], None, "None, with fallback Test")
        test([token.token_file], [token.token_file], [token.token_config], "TokenFile, with fallback Test")
        test([token.token_file], [token.token_file], [token.token_config, None], "TokenFile, with fallback Test with None")
        test([token.token_file], [token.token_file, None], [token.token_config], "TokenFile and None, with fallback Test")

    def test__format_as_bearer_token(self):
        """ Make sure that the token can be wrapped as a bearer token correctly """
        # pylint: disable=C0301 # lambdas must be on one line
        test = lambda expected, given, msg : self.assertEqual(expected, token._format_as_bearer_token(given), msg)
        test("Bearer ", "", 'blank given')
        test("Bearer None", None, 'nothing given')
        test("Bearer token-here", 'token-here', 'token given')

    @patch('urllib.request.urlopen')
    def test_read_tokens(self, urlopen_mock):
        """
        Test the read_tokens function, make sure that the data that comes back
        is parsed correctly and in the correct format
        """
        # Setup for tests
        user = 'tester'
        token_lambdas = [token.token_config]
        config = {'cmr.token.value':'pass'}

        self.assertEqual(None, token.read_tokens(None, token_lambdas=[]))
        self.assertEqual(None, token.read_tokens(None,
            token_lambdas=token_lambdas,
            config={'cmr.token.value':''}))

        # Setup for a good test
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/token_good.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)

        result = token.read_tokens(user, token_lambdas, config)
        self.assertEqual(1, result['hits'], "Hits test")

        items = result['items']
        self.assertEqual(1, len(items), "item count test")

        access_token = items[0]['access_token']
        self.assertEqual("EDL-UToken-Content", access_token, "Access token test")

        experation = result['items'][0]['expiration_date']
        self.assertEqual('10/31/2121', experation, "experation date test")

        experation_date = datetime.strptime(experation, '%m/%d/%Y')
        self.assertTrue(datetime.now() < experation_date, "experation date is in future")

        # ##############################
        # Now test a bad call
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/token_bad.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file, status=401)
        result = token.read_tokens(user, token_lambdas, config)
        self.assertEqual('invalid_credentials', result['error'], "check bad response")

    @patch('urllib.request.urlopen')
    def test_create_token(self, urlopen_mock):
        """ Test that the code can send a create token request """

        self.assertEqual(None, token.create_token(None, token_lambdas=[]), "No lambdas")

        user = 'tester'
        token_lambdas = [token.token_config]

        config = {'cmr.token.value':''}
        self.assertEqual(None, token.create_token(None,
            token_lambdas=token_lambdas,
            config=config), "No password")

        config = {'cmr.token.value':'pass'}

        # Setup for a good test
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/create_token_good.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)
        tokens = token.create_token(user, token_lambdas, config)
        self.assertEqual('EDL-UToken-Content', tokens['access_token'], 'access token test')

        # Setup for a bad test
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/create_token_bad.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)
        tokens = token.create_token(user, token_lambdas, config)
        self.assertEqual('invalid_credentials', tokens['error'], 'Bad test')

    @patch('urllib.request.urlopen')
    def test_delete_token(self, urlopen_mock):
        """ Test that the code can send a delete token request to EDL """

        self.assertEqual(None, token.delete_token(None, None, token_lambdas=[]))

        user = 'tester'
        token_lambdas = [token.token_config]
        config = {'cmr.token.value':''}

        self.assertEqual(None,
            token.delete_token(None, None,
                token_lambdas=[],
                config=config),
            "empty password")

        self.assertEqual(None,
            token.delete_token(None, None,
                token_lambdas=[token.token_config],
                config=config),
            "empty password - lambda")

        config = {'cmr.token.value':'pass'}

        # Setup for a good test
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/revoke_token_good.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)
        tokens = token.delete_token('EDL-UToken-Content', user, token_lambdas, config)
        self.assertEqual({'http-headers':{}}, tokens, 'access token test')

        # Setup for a bad test
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/create_token_bad.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)
        tokens = token.delete_token('EDL-UToken-Content', user, token_lambdas, config)
        self.assertEqual('invalid_credentials', tokens['error'], 'Bad test')

    @patch('urllib.request.urlopen')
    @patch('cmr.auth.token.read_tokens')
    @patch('cmr.auth.token.delete_token')
    @patch('cmr.util.common.now')
    def test_fetch_token_delete_path(self, now_mock, deltoken_mock, readtoken_mock, urlopen_mock):
        """ Test that the code can fetch expired tokens and then try to delete one """

        token_lambdas = [token.token_config]
        user = 'tester'
        config = {'cmr.token.value':'pass'}

        #now_mock.return_value = datetime.strptime('12/28/2021 09:13:20 UTC', '%m/%d/%Y %H:%M:%S %Z')
        now_mock.return_value = datetime(2021, 12, 28, 9, 13, 20, 0)
        self.assertEqual(datetime(2021, 12, 28, 9, 13, 20, 0), common.now())
        self.assertEqual(1640700800.0, common.now().timestamp(),
            'time must be frozen for this to work')

        # create old data response - expired tokens
        recorded_data_file_old = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/tokens_old.json')
        recorded_data_old = common.read_file(recorded_data_file_old)
        old = json.loads(recorded_data_old)

        # create good data response - new tokens
        recorded_data_good = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/token_good.json')
        recorded_data_good = common.read_file(recorded_data_good)
        good = json.loads(recorded_data_good)

        # setup responses
        readtoken_mock.side_effect = [old, good, good]

        recorded_data_file_good = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/create_token_good.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file_good)

        deltoken_mock.return_value = "dummy"

        # run test
        tokens = token.fetch_token(user, token_lambdas, config)
        self.assertEqual('EDL-UToken-Content', tokens, 'access token test')

    @patch('urllib.request.urlopen')
    def test_fetch_token(self, urlopen_mock):
        """ Test that the code can fetch a token request """

        self.assertEqual(None, token.fetch_token(None, token_lambdas=[]))

        token_lambdas = [token.token_config]
        config = {'cmr.token.value':''}
        self.assertEqual(None, token.fetch_token(None, token_lambdas=token_lambdas, config=config))

        user = 'tester'
        config = {'cmr.token.value':'pass'}

        # Setup for a good test
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/token_good.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)
        tokens = token.fetch_token(user, token_lambdas, config)
        self.assertEqual('EDL-UToken-Content', tokens, 'access token test')

        # Setup for a bad test
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/token_bad.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)
        tokens = token.fetch_token(user, token_lambdas, config)
        self.assertEqual('invalid_credentials', tokens['error'], 'Bad test')

    @patch('urllib.request.urlopen')
    @patch('cmr.auth.token.read_tokens')
    def test_fetch_token2(self, readtoken_mock, urlopen_mock):
        """ Test that the code can fetch a token request """

        self.assertEqual(None, token.fetch_token(None, token_lambdas=[]))

        token_lambdas = [token.token_config]
        config = {'cmr.token.value':''}
        self.assertEqual(None, token.fetch_token(None, token_lambdas=token_lambdas, config=config))

        user = 'tester'
        config = {'cmr.token.value':'pass'}

        # Setup for an empty test
        readtoken_mock.return_value = {'hits':0, 'items':[]}
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/create_token_good.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)
        tokens = token.fetch_token(user, token_lambdas, config)
        self.assertEqual('EDL-UToken-Content', tokens, 'access token test')

    @patch('urllib.request.urlopen')
    def test_fetch_bearer_token(self, urlopen_mock):
        """ Test that the code can fetch a token request """
        user = 'tester'
        token_lambdas = [token.token_config]
        config = {'cmr.token.value':'pass'}

        # Setup for a good test
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/token_good.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)
        tokens = token.fetch_bearer_token(user, token_lambdas, config)
        self.assertEqual('Bearer EDL-UToken-Content', tokens['authorization'], 'access token test')

        tokens = token.fetch_bearer_token(user, token_lambdas)
        self.assertEqual({"error":"No lambda could providede a token"}, tokens,
            'no token found from config when no config given')

        # Setup for a bad test
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/token_bad.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)
        tokens = token.fetch_bearer_token(user, token_lambdas, config)
        self.assertEqual('invalid_credentials', tokens['error'], 'Bad test')

    @patch('urllib.request.urlopen')
    def test_fetch_bearer_token_with_password(self, urlopen_mock):
        """ Test that the code can fetch a token request """

        # Setup for a good test
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/token_good.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)
        tokens = token.fetch_bearer_token_with_password('tester', "pass")
        self.assertEqual('Bearer EDL-UToken-Content', tokens['authorization'], 'access token test')


    @patch('urllib.request.urlopen')
    def test_use_bearer_token_from_url(self, urlopen_mock):
        """ Follow the path in the use_bearer_token() which pulls from a url """
        # Setup for use bearer token
        config = {'cmr.token.value':'pass'}
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/token_good.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)
        expected = {'cmr.token.value': 'pass', 'authorization': 'Bearer pass'}
        self.assertEqual(expected, token.use_bearer_token(config=config))

    @patch('urllib.request.urlopen')
    def test_token(self, urlopen_mock):
        """ Test that the code can fetch a token request """
        token_lambdas = [token.token_config]
        config = {'cmr.token.value':'EDL-UToken-Content'}

        # Setup for a good test
        recorded_data_file = os.path.join (os.path.dirname (__file__),
                                           '../../data/edl/token_good.json')
        urlopen_mock.return_value = valid_cmr_response(recorded_data_file)
        tokens = token.token(token_lambdas, config)
        self.assertEqual('EDL-UToken-Content', tokens, 'access token test')

    @patch('cmr.util.common.execute_command')
    def test_password_manager(self, cmd_mock):
        """ Test a valid login using the password manager """
        expected_token = "Secure-Token"
        options = {}
        cmd_mock.return_value = expected_token
        self.assertEqual(expected_token, token.token_manager(options))

        actual = str(token.token(token.token_manager, options))
        self.assertEqual (expected_token, actual)

    @patch('cmr.util.common.execute_command')
    def test_request_token_two_ways(self, cmd_mock):
        """
        Try to get the token using two different handlers. The file handler
        should fail fall back to the manager which will pass
        """
        options = {'cmr.token.file': "/tmp/__fake-file-never-existed.txt"}
        expected = "Secure-Token"
        cmd_mock.return_value = expected

        # try file first, then manager
        actual = token.token([token.token_manager,token.token_file], options)
        self.assertEqual(expected, actual)

        # try the other way around
        actual = token.token([token.token_file,token.token_manager], options)
        self.assertEqual(expected, actual)

    def test_help_full(self):
        """Test the built in help"""
        result_full = token.help_text()
        self.assertTrue (-1<result_full.find("token_file"))
        self.assertTrue (-1<result_full.find("token("))

    def test_help_less(self):
        """Test the built in help for filtering"""
        result_less = token.help_text("token_")
        self.assertTrue (-1<result_less.find("token_file"))
        self.assertFalse (-1<result_less.find("token()"))

if __name__ == '__main__':
    unittest.main()
