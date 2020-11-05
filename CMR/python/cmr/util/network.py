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

#date 2020-11-05
#since 0.0

import re
import socket
import urllib.request

def get_local_ip():
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
    except socket.error as _:
        # try another way to do this
        ip_address = get_public_ip()
    return ip_address

def get_public_ip():
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
