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
A Library for managing EDL tokens to be used with CMR
date: 2020-10-26
since: 0.0

Overview:
    The function token(lambda_list, config) will iterate over a list of token
    managers and return the value from the first manager that finds a token.

    Token Managers are lambda functions that take in a 'config' dictionary for
    use as a source for configurations, and returns a token as a string.
"""

import os
import subprocess
from typing import Callable
import cmr.util.common as common

# ##############################################################################
# lambdas

# All password lambda functions accept two parameters and return a string
# Parameters:
#   user_id:string - Earth Data Login user name
#   config:dictionary - configuration object which may be used by the lambda
# Returns:
#   password:string

def token_literal(token_text: str) -> Callable:
    """
    Generates an token lambda file which always returns the same value, this is
    used for testing, and also as an example of how to write token managers
    Parameters:
        token_text(string): the token which should always be returned by the lambda
    Return:
        A lambda function which takes a dictionary and returns a token
    """
    return lambda _ : token_text


# document-it: {"key":"cmr.token.value", "default":"None"}
def token_config(config: dict = None) -> str:
    """
    Pull a token from the configuration dictionary
    Parameters:
        config: Responds to:
            "cmr.token.value": value of token, defaults to 'None'
    """
    config = config if isinstance(config, dict) else {}
    value = config.get('cmr.token.value', None)
    return value


# document-it: {"key":"cmr.token.file", "default":"~/.cmr_token"}
def token_file(config: dict = None) -> str:
    """
    Load a token from a local user file assumed to be ~/.cmr_token
    Parameters:
        config: Responds to:
            "cmr.token.file": location of token file, defaults to ~/.cmr_token
    Returns
        token from file
    """
    config = config if isinstance(config, dict) else {}
    path_to_use = config.get('cmr.token.file', '~/.cmr_token')
    path = os.path.expanduser(path_to_use)
    clear_text = common.read_file(path)
    return clear_text


# document-it: {"key":"token.manager.account", "default":"user"}
# document-it: {"key":"token.manager.service", "default":"cmr-lib-token"}
# document-it: {"key":"token.manager.app", "default":"/usr/bin/security"}
def token_manager(config: dict = None) -> str:
    """
    Use a system like the MacOS X Keychain app. Any os which also has the
    security app would also work.
    Parameters:
        config: Responds to the following:
            'token.manager.account': account field in Keychain
            'token.manager.app': Keychain command - defaults to /usr/bin/security
            'token.manager.service' defaults to 'cmr-lib-token'
    Returns:
        token from Keychain
    """
    try:
        config = config if isinstance(config, dict) else {}
        account = config.get('token.manager.account', 'user')
        service = config.get('token.manager.service', 'cmr-lib-token')
        app = config.get('token.manager.app', '/usr/bin/security')
        result = common.call_security(account, service, app)
    except subprocess.CalledProcessError:
        result = None
    return result

# ##############################################################################
# functions

def token(token_lambdas=None, config:dict = None) -> str:
    """
    Recursively calls lambdas till a token is found
    Parameters:
        token_lambda: a token lambda or a list of functions
        config: Responds to no values
    Returns:
        the EDL Token from the token lambda
    """
    if token_lambdas is None:
        token_lambdas = [token_file,token_config]
    if not isinstance(token_lambdas, list):
        token_lambdas = [token_lambdas]

    handler = token_lambdas.pop()
    edl_token = handler(config)
    if edl_token is None and len(token_lambdas)>0:
        edl_token = token(token_lambdas, config)
    return edl_token

def help_text(prefix:str = '') -> str:
    """
    Built in help - prints out the public function names for the token API
    Parameters:
        filter: filters out functions beginning with this text, defaults to all
    Returns:
        text ready to be passed to print()
    """
    formater = common.help_format_lambda(prefix)

    out = __doc__

    out += ('\n**** Functions:\n')
    for item in [help_text, token]:
        out += formater(item.__name__ + '()', item)

    out += '\n**** Token Lambdas:\n'
    for item in [token_literal, token_config, token_file, token_manager]:
        out += formater(item.__name__, item)
    return out
