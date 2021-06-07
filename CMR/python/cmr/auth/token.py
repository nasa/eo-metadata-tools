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

import cmr.util.common as common

# ##############################################################################
# lambdas

# All password lambda functions accept two parameters and return a string
# Parameters:
#   user_id: string - Earth Data Login user name
#   config: dictionary - configuration object which may be used by the lambda
# Returns:
#   password: string

def token_literal(token_text: str):
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
def token_config(config: dict = None):
    """
    Pull a token from the configuration dictionary
    Parameters:
        config: Responds to:
            "cmr.token.value": value of token, defaults to 'None'
    """
    config = common.always(config)
    value = config.get('cmr.token.value', None)
    return value

# document-it: {"key":"env", "default":"", "msg":"uat, ops, prod, production, or blank for ops"}
def _env_to_extention(config: dict = None):
    """
    Allow different files to be loaded for each environment, make an env
    extension which will be appended to the token file path
    Parameters:
        config dictionary containing an env value
    Return:
        empty string or a dot followed by the environment.
    """
    config = common.always(config)

    env = config.get('env', '')
    if env is None:
        env = ''
    env = env.lower().strip()
    if len(env)>0 and env.endswith("."):
        env = env[:-1]
    if env in ['', 'ops', 'prod', 'production']:
        env = "" # no extension
    else:
        env = "." + env
    return env

# document-it: {"key":"cmr.token.file", "default":"~/.cmr_token"}
# document-it: {"from":"._env_to_extention"}
def _token_file_path(config: dict = None):
    """
    Return the path to the file which stores a CMR token. This path can be different
    for each environment if specified with the env config.
    Returns
        ~/.cmr_token<.env>, no env if production
    """
    config = common.always(config)
    env_extention = _env_to_extention(config)
    path_to_use = config.get('cmr.token.file', '~/.cmr_token' + env_extention)
    return path_to_use

# document-it: {"from":".token_file_path"}
def token_file(config: dict = None):
    """
    Load a token from a local user file assumed to be ~/.cmr_token
    Parameters:
        config: Responds to:
            "cmr.token.file": location of token file, defaults to ~/.cmr_token
                for production, followed by a dot and the environment name if
                specified.
            "env": if not production, appended to the end of ~/.cmr_token with a dot
    Returns
        token from file
    """
    path_to_use = _token_file_path(config)

    path = os.path.expanduser(path_to_use)
    clear_text = None
    raw_clear_text = common.read_file(path)
    if raw_clear_text is not None:
        for line in raw_clear_text.splitlines():
            if not line.startswith("#"):
                clear_text = line
                break # we only need the first one
    return clear_text

# document-it: {"key":"token.manager.account", "default":"user"}
# document-it: {"key":"token.manager.service", "default":"cmr-lib-token"}
# document-it: {"key":"token.manager.app", "default":"/usr/bin/security"}
def token_manager(config: dict = None):
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
        config = common.always(config)
        account = config.get('token.manager.account', 'user')
        service = config.get('token.manager.service', 'cmr-lib-token')
        app = config.get('token.manager.app', '/usr/bin/security')
        result = common.call_security(account, service, app)
    except subprocess.CalledProcessError:
        result = None
    return result

# ##############################################################################
# functions

def use_bearer_token(token_lambdas = None, config:dict = None):
    """
    Create a new config dictionary, optionally based on a supplied one, and add
    the bearer token to the config object abstracting away as many details as
    possible.
    Parameters:
        token_lambda: a token lambda or a list of functions
        config: config dictionary to base new dictionary off of
    Returns:
        new config dictionary with Bearer token assigned as an 'authorization'
    """
    if config is None:
        config = {}
    augmented_config = config.copy()
    bearer_token = bearer(token_lambdas, config)
    augmented_config["authorization"] = bearer_token
    return augmented_config

def bearer(token_lambdas = None, config: dict = None):
    """
    Loops through the list of lambdas till a token is found. These lamdba functions
    return an EDL token which can be passed to Earthdata software to authenticate
    the user. To get a token, go to https://sit.urs.earthdata.nasa.gov/user_tokens
    Token is returned as a Bearer String

    Parameters:
        token_lambda: a token lambda or a list of functions
        config: Responds to no values
    Returns:
        the EDL Bearer Token from the token lambda
    """
    token_value = token(token_lambdas, config)
    if token_value is not None and len(token_value)>0:
        token_value = "Bearer " + token_value
    return token_value

def token(token_lambdas = None, config: dict = None):
    """
    Loops through the list of lambdas till a token is found. These lamdba functions
    return an EDL token which can be passed to Earthdata software to authenticate
    the user. To get a token, go to https://sit.urs.earthdata.nasa.gov/user_tokens

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

def help_text(prefix: str = '') -> str:
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
