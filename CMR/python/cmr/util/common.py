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

#date 2020-10-26
#since 0.0

def dict_or_default(dictionary, key, default):
    """
    return the contents of a dictionary pointed to with a key, or a default
    value. The default can either be a raw value or a pointer to a function
    that will return the default
    dictionary(dictionary)= thing to check
    key(string)= index in dictionary to look for
    default(string/lambda)= text or function that gets text to use if value does not exist
    """
    if key in dictionary:
        ret = dictionary[key]
    else:
        if hasattr(default, '__call__'):
            # Python > 3.2 way of doing things
            ret = default()
        #elif callable(default):
        #    ret = default()
        else:
            ret = default
    return ret
