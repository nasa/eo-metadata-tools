"""
Demonstrate how to perform a variable search
"""

import argparse
import sys
import cmr.util.network as net
import cmr.search.common as scom

def get_block_of_records(search, env=None):
    """ Make the GET call for variables using the low level network code """

    #curl https://cmr.sit.earthdata.nasa.gov/search/variables
    #?keyword=C1200371866-DEMO_PROV
    #&pretty=true

    # build a url
    if env is None:
        env = 'sit' # assume SIT and not OPS because that is where the data is
    url = scom.cmr_basic_url(base='variables', query=search, config={'env':env})

    print(f'Using {url} for network example.')

    # setup headers and inputs
    accept = "application/vnd.nasa.cmr.umm_results+json"
    headers = {}

    #make call
    result = net.get(url, accept=accept, headers=headers)
    items = result.get("items", [])
    return items

def process_records(title, records):
    """ Find unique collection ids and print them out """
    processed_records = {}
    for item in records:
        meta = item["meta"]
        umm = item["umm"]
        cid = meta["concept-id"]
        var_name = umm["Name"]
        processed_records[cid] = var_name
    print (f'\n## {title} ##')
    print (f'* Returned item count: {len(records)}')
    print (f'* Uniq keys: {len(processed_records.keys())}')
    print (f'* {processed_records}')

def use_low_level_network(query, env):
    """ Make a call for variables using the lower level network code """
    records = get_block_of_records(query, env=env)

    process_records("Network example", records)

def use_common_search(query, env):
    """ Make variable call using the common search code based on the network code. """
    config = {'env': env}

    scom.set_logging_to(scom.logging.DEBUG)
    records = scom.search_by_page("variables", query=query, config=config)
    process_records("Common Search Example", records)

def get_options(args=None):
    """ Setup and collect command line arguments """
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description='Example script showing how to download variables.')
    parser.add_argument('-e', '--environment',
        help='set environment, SIT (default), UAT, OPS, PROD, localhost')
    parser.add_argument('-n', '--network', action='store_true',
        help='run network code example')
    parser.add_argument('-q', '--query', help='keyword query to run')
    parser.add_argument('-s', '--search', action='store_true',
        help='run common search code example (default)')
    options = parser.parse_args(args)
    return options

def main():
    """ Respond to a command line run """
    options = get_options()
    env = options.environment.lower() if options.environment else 'sit'

    if options.query:
        query = {"keyword": options.query}
    else:
        query = {"keyword": "C1200371866-DEMO_PROV"}

    nothing_ran = True
    if options.network:
        use_low_level_network(query, env)
        nothing_ran = False
    if options.search or nothing_ran:
        use_common_search(query, env)
        nothing_ran = False

if __name__ == '__main__':
    main()
