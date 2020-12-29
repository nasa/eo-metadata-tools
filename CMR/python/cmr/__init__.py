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
A Library interfacing with the CMR API
date: 2020-11-23
since: 0.0

Create version info Query the BUILD constant for information on the package version

More information can be found at:
https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html

"""
import re
import subprocess
from datetime import datetime as dt

BUILD = {'BUILD_REF': '{BUILD_REF}',
    'BUILD_DATE': '{BUILD_DATE}',
    'BUILD_VERSION': '{BUILD_VERSION}'}

""" Clean up the dictionary for the case where the code is run locally """
#pylint: disable=W0703
try:
    if BUILD['BUILD_REF'].find('BUILD_REF'):
        # Ask git for the current version
        BUILD['BUILD_REF'] = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
            stdout=subprocess.PIPE, check=True).stdout.decode("utf-8").strip()
    if BUILD['BUILD_DATE'].find('BUILD_DATE'):
        BUILD['BUILD_DATE'] = dt.now().isoformat()
        del dt
    if BUILD['BUILD_VERSION'].find('BUILD_VERSION'):
        # look for version in the setup.py file, example line: version="0.0.1",
        with open ('setup.py') as file_obj:
            LINE = None
            for LINE in file_obj:
                if LINE.find("version=") > 0:
                    PATTERN = r'.*version=[\'\"]?([0-9.]+)[\'\"]?,.*'
                    ver = re.sub(PATTERN, '\\1', LINE).strip()
                    BUILD['BUILD_VERSION'] = ver
                    del ver
                    del PATTERN
                    break
            del LINE
        del file_obj
except Exception as exc:
    # catch any error and just move on
    print ("Could not create build info: " + exc)
