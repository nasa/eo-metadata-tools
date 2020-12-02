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
A basic wrapper for the python logging API
date 2020-11-24
since 0.0
"""

import logging

def set_logging_file(file_name):
    """ Sets the file to write logs to"""
    logging.basicConfig(filename=file_name)

def set_logging_to(level=logging.ERROR):
    """ Sets the logging level to the value provided, or default to ERROR """
    logging.basicConfig(level=level)

def set_logging_to_warn():
    """ Sets the logging level to warn """
    logging.basicConfig(level=logging.WARN)

def set_logging_to_info():
    """ Sets the logging level to info """
    logging.basicConfig(level=logging.INFO)

def set_logging_to_debug():
    """ Sets the logging level to debug """
    logging.basicConfig(level=logging.DEBUG)

# *****************************************************************************
# Run once

set_logging_to()
