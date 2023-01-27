"""
A very short demo of how to use the provider API
"""

from functools import partial

import cmr.search.providers as p

# be like clojure, calculate text once
print_line = partial(print, "*" * 80)

print(p.search_by_id(None))

print_line()
print(p.search_by_id(''))

print_line()
print(p.search_by_id('.*GHRC.*'))

print_line()
print(p.search_by_id('*GHRC*'))

print_line()
print(p.search_by_id('.*GHRC.*', {'env':'uat'}))

print_line()
result = p.search_by_id('.*GHRC.*', {'env':'uat'})
if 'errors' in result:
    print('found errors')
else:
    print (len(result))
