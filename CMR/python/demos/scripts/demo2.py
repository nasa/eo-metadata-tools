#!/usr/bin/env python3

"""A simple test of the API as a library"""

#import cmr.search.collection as coll
try:
    # Try loading the code from the python environment
    import cmr.search.granule as gran
except ModuleNotFoundError:
    # Try to load the local system
    import os
    import sys
    sys.path.append(os.path.expanduser('.'))
    import cmr.search.granule as gran

# Terminal colors
def text_color(msg='{}', color='\033[0;37m'):
    """Defaults to White"""
    no_color = '\033[0m'
    return '{}{}{}'.format(color, msg, no_color)
def style_error(msg='{}'):
    """Set text to red"""
    red_code = '\033[0;31m'
    return text_color(msg, red_code)
def style_output(msg='{}'):
    """Set text to green"""
    green_code = '\033[0;32m'
    return text_color(msg, green_code)
def style_info(msg='{}'):
    """Set text to blue"""
    blue_code = '\033[0;34m'
    return text_color(msg, blue_code)

# Get to work
def main():
    """The main function"""
    params = {'provider': 'ORNL_DAAC', 'polygon': '10,10,30,10,30,20,10,20,10,10'}
    print (style_info('Searching for {}').format(params))

    output_results = gran.experimental_search_generator(params, limit=9000, config={'env':'uat'})
    if output_results is None:
        print (style_error("no results returned"))
    else:
        output_format = style_output()

        count = 0
        uniq = {}
        for item in output_results:
            count += 1
            cid = item['meta']['concept-id']
            if not cid in uniq:
                uniq[cid] = 0
            uniq[cid] += 1

            print (output_format.format(cid), end=", ")
        print ('.')
        print (count)
        print (len(uniq.keys()))

if __name__ == '__main__':
    main()
