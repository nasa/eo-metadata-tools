"""
NASA EO-Metadata-Tools Python interface for the Common Metadata Repository (CMR)

    https://github.com/nasa/Common-Metadata-Repository/

Copyright (c) 2020 United States Government as represented by the Administrator
of the National Aeronautics and Space Administration. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
# Library for generating EDL tokens from CMR
# date: 2020-10-26
# since: 0.0

#import base64
import json
import os
import re
import socket
import subprocess
import time
import urllib.parse
import urllib.request

import cmr.util.common as c

# ##############################################################################
# local utilities

def _get_local_ip():
    """
    Note, this function may not always work for all users on all operating
    systems.
    Returns:
        Computer's IP address, or the public IP address, or 127.0.0.1
    """
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        socket.close()
    except:
        # try another way to do this
        ip_address = _get_public_ip()
    return ip_address

def _get_public_ip():
    """
    Check with an external site to get the public IP address
    Returns:
        Public IP address or 127.0.0.1 if there was an error
    """
    data = str(urllib.request.urlopen('http://checkip.dyndns.com/').read())
    found = re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data)
    if found is not None:
        return found.group(1)
    return "127.0.0.1"

def _read_file(path):
    """
    Read and return the contents of a file
    Parameters:
        path (string): full path to file to read
    Returns:
        None if file was not found, contents otherwise
    """
    if os.path.isfile(path):
        file = open(path, "r")
        text = file.read().strip()
        file.close()
    else:
        text = None
    return text

def _write_file(path, text):
    """
    Write (creating if need be) file and set it's content
    Parameters:
        path (string): path to file to write
        text (string): content for file
    """
    path = os.path.expanduser(path)
    cache = open(path, "w+")
    cache.write(text)
    cache.close()

def _write_token_file(token_text, options=None):
    """
    Write out a token cache file
    Parameters:
        token_text (string) : content to write out
        options (dictionary): overrides, responds to 'cmr.token.file'
    """
    if options is None:
        options = {}
    token_path = c.dict_or_default(options, "cmr_token_file", "~/.cmr_token")
    _write_file(token_path, token_text)

def _days_old_from_time(past_timestamp, current_timestamp=time.time(), age=1.0):
    """
    tests if a difference between timestamps are old
    Parameters:
        past_timestamp(float): timestamp of file
        current_timestamp(float): default to now, timestamp
        age(float): defaults to 1.0, days old
    Returns:
        true if the file is older then age
    """
    days_old = (current_timestamp - past_timestamp)/60.0/60.0/24.0
    return days_old > age

def _old_file(path):
    """
    non-pure function
    to get age of a file from today
    Parameters:
        path(string): path to file to test
    Returns:
        true if the file is older then one day
    """
    return _days_old_from_time(os.path.getmtime(path))

def _read_token_file(options=None):
    """
    load a password from a local user file assuming ~/.password
    Parameters:
        options(dictionary): responds to 'cmr.token.file'
    Returns:
        content of token file, None if it does not exist
    """
    if options is None:
        options = {}
    raw_path = c.dict_or_default(options, "cmr.token.file", "~/.cmr_token")
    path = os.path.expanduser(raw_path)
    clear_text = None if _old_file(path) else _read_file(path)
    return clear_text

def _execute_command(cmd):
    """
    a utility method to execute a shell command and return a string of the output
    Parameters:
        cmd(string) unix command to execute
    Returns:
        response from command
    """
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return result.stdout.decode('utf-8')

# ##############################################################################
# lambdas

# All password lambda functions accept two parameters and return a string
# Parameters:
#   user_id(string): Earth Data Login user name
#   options(dictionary): configuration object which may be used by the lambda
# Returns:
#   password

def password(clear_password):
    """
    create a pass through lambda function to allow plain text passwords, not an
    encouraged act however
    Parameters:
        clear_password(string): password
    Returns:
        A lambda function with conforms to the definition
    """
    return lambda id, opt : clear_password

def password_file(_, options=None):
    """
    load a password from a local user file assuming ~/.cmr_password
    """
    if options is None:
        options = {}
    path_to_use = c.dict_or_default(options, "password.path", "~/.cmr_password")
    path = os.path.expanduser(path_to_use)
    if os.path.isfile(path):
        clear_text = _read_file(path)
    else:
        clear_text = None
    return clear_text

def password_manager(account, options=None):
    """
    Use a system like the MacOS X Keychain app. Any os which also has the
    security app would also work.
    Responds to 'password.manager.app' and 'password.manager.service'
    """
    if options is None:
        options = {}
    app = c.dict_or_default(options, "password.manager.app", "/usr/bin/security")
    service = c.dict_or_default(options, "password.manager.service", "cmr-lib")
    cmd = [app, "find-generic-password", "-a", account, "-s", service, "-w"]
    result = _execute_command(cmd)
    if result is not None:
        result = result.strip()
    return result

# ##############################################################################
# functions

def sit():
    """ User to return the URL part that points to SIT """
    return "sit."

def uat():
    """ User to return the URL part that points to UAT """
    return "uat."

def prod():
    """ User to return the URL part that points to production """
    return ""

def _request_token(user, options):
    """
    internal worker function to call CMR and request a token
    Parameters:
        user(string): EDL user name
        password(string): EDL password
        use_cache(boolean): True if tokens are to be cached and reused
        client_name: HTTP client name to use in communications
        env(string): CMR environment, defaults to prod
        client_address(string): ip address of the machine making the request for token
    Returns:
        token or text of exceptions from HTTPError
    """
    #unpack
    clear_password = options["clear_text_password"]
    use_cache = options["cached"]
    client_name = options["client_name"]
    env = options["env"]
    client_address = options["address"]

    if use_cache:
        token_text = _read_token_file()
    else:
        token_text = None
    if token_text is not None and len(token)>0:
        return token_text
    env = env if env.endswith(".") else env + "."
    data='<token>\
<username>{}</username>\
<password>{}</password>\
<client_id>{}</client_id>\
<user_ip_address>{}</user_ip_address>\
</token>'.format(user, clear_password, client_name, client_address)

    url='https://cmr.{}earthdata.nasa.gov/legacy-services/rest/tokens.json'.format(env)
    encoded_data = str.encode(data)
    req = urllib.request.Request(url, data=encoded_data)
    req.add_header('Content-Type', 'application/xml')
    req.add_header('User-Agent', client_name)
    try:
        resp = urllib.request.urlopen(req)
        obj_json = json.loads(resp.read().decode('utf-8'))

        token_text = obj_json['token']['id']
        if use_cache:
            _write_token_file(token_text)
        return token_text
    except urllib.error.HTTPError as exception:
        return exception

def token(edl_user_name, password_lambda=password_file, opts=None):
    """
    Requests an Earth Data Login Token from CMR
    Parameters:
        edl_user_name(string): EDL user name
        password_lambda(lambda): function for returning password
        opt(dictionary): dictionary of options
    Returns:
        token or text of exceptions from HTTPError
    """

    # handle the default, don't pass in bad data to the internal handler
    if opts is None:
        opts = {}
    clean={"env": c.dict_or_default(opts, "cmr.env", prod()),
        "address": c.dict_or_default(opts, 'client.address', _get_local_ip),
        "client_name": c.dict_or_default(opts, 'client.name', 'python_cmr_lib'),
        "cached": c.dict_or_default(opts, "cache.token", True),
        "clear_text_password": password_lambda(id, opts)}

    edl_token = _request_token(edl_user_name, clean)
    #    clear_text_password,
    #    cached,
    #    client_name,
    #    env=env,
    #    client_address=address)
    return edl_token

def print_help(prefix=""):
    """
    Built in help - prints out the public function names
    Parameters:
        filter(string): filters out functions beginning with this text, defaults to all
    """
    layout = "\n%s:\n%s\n"
    # n=name, c=content
    out = lambda n, c : print (layout % (n, c.__doc__.strip())) if n.startswith(prefix) else None

    print ("**** Functions:")
    out("helout()", help)
    out("token(id, lambda, options)", token)
    out("sit()", sit)
    out("uat()", uat)
    out("prod()", prod)
    print ("**** Password Lambdas:")
    out("password(password)", password)
    out("password_file", password_file)
    out("password_manager", password_manager)
