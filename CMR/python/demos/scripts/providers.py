"""
A very short demo of how to use the provider API
"""

import cmr.search.providers as p

print(p.search_by_id(None))

print ("*"*80)
print(p.search_by_id(''))

print ("*"*80)
print(p.search_by_id('.*GHRC.*'))

print ("*"*80)
print(p.search_by_id('*GHRC*'))

print ("*"*80)
print(p.search_by_id('.*GHRC.*', {'env':'uat'}))

print ("*"*80)
result = p.search_by_id('.*GHRC.*', {'env':'uat'})
if 'errors' in result:
    print('found errors')
else:
    print (len(result))
