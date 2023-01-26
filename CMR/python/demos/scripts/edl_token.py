"""
A very short script showing how to use a file defined token from EDL. Pass in
the path to the file containing nothing but the EDL token as the first and only
parameter to the script. This will be read by the token library and included in
the config dictionary.
"""

import sys

import cmr.search.collection as coll
import cmr.auth.token as t

########################################
# Basic inputs for search
params = {'keyword': 'fish food'}
configurations={'env':'sit'}

########################################
# Basic search with no token
public_count = len(coll.search(params, limit=500, config=configurations))
print (f"Records when not logged in: {public_count}")

########################################
# Add token to config
if len(sys.argv)>1:
    configurations['cmr.token.file'] = '~/.pw/urs.token.sit'
    print ("\nUsing a token from user specificed file...")
configurations = t.use_bearer_token(config=configurations)

########################################
# Basic search, now WITH a token
private_count = len(coll.search(params, limit=500, config=configurations))
print (f"Records when logged in: {private_count}")

########################################
# Conclusion
if public_count != private_count:
    print ("\nLogging in results in a different number of records.")
