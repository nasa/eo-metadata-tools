"""
Demonstrate how to perform a scroll call to CMR
"""

import cmr.util.network as net

def get_block_of_records(search, scroll_id=None):
    """
    Recursive function to return records from CMR using scroll. The first time
    The function is called, just send a dictionary of what your looking for.
    This function will call itself as many times as needed to collect all the
    records and return them in a list. When calling recursively, send the
    scroll id
    """
    url = "https://cmr.uat.earthdata.nasa.gov/search/collections.umm_json"
    accept = "application/vnd.nasa.cmr.umm_results+json"
    body = search.copy()
    if scroll_id is None:
        # first time here, request a scroll id and clear out headers
        body.update({"scroll": "true", "page_size": "50"})
        headers = {}
    else:
        # recursive call, set the scroll id and don't touch the body
        headers = {"CMR-Scroll-Id": str(scroll_id)}

    result = net.post(url, body, accept=accept, headers=headers)
    items = result.get("items", [])
    count = len(items)  # will be zero if we are at the end
    resp_headers = result.get("http-headers", {})
    scroll_id = resp_headers.get("CMR-Scroll-Id", "")
    results = []

    if count > 0:
        # probably not done yet, try one more time. This time, send the scroll id
        results = get_block_of_records(search, scroll_id=scroll_id)
        results.extend(items)   # add the recursive call records to this calls
    else:
        # no records came back, work is done, tell CMR it can clear scroll
        url_clear = "https://cmr.uat.earthdata.nasa.gov/search/clear-scroll"
        headers['Content-Type'] = 'application/json'
        data = '{"scroll_id": "' + str(scroll_id) + '"}'
        net.post(url_clear, data, accept=None, headers=headers)
    return results

def main():
    """
    Test the function and verify that it is returning unique records
    """
    records = get_block_of_records({"keyword": "food"})
    print (f'returned items: {len(records)}')

    processed_records = {}
    for item in records:
        meta = item["meta"]
        umm = item["umm"]
        cid = meta["concept-id"]
        short_name = umm["ShortName"]
        processed_records[cid] = short_name

    print (f'uniq keys: {len(processed_records.keys())}')

if __name__ == '__main__':
    main()
