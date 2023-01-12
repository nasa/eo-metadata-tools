"""
Iterates over cmr-graphql (https://github.com/nasa/cmr-graphql/) to
retrieve all of the collection's concept-ids from a given env (SIT, UAT, PROD)
a valid token must be passed
as an env variable otherwise only what is publicly available will be able to be fetched
then print the list of these concepts to a local file
"""
import os
import requests
import sys
import logging

# Set logging
logging.basicConfig(level=logging.DEBUG)

token = os.getenv('TOKEN')

endpoint = os.getenv('GRAPHQL_URL', 'https://graphql.earthdata.nasa.gov/api')

# Bearer may be needed before the token in your env var
# if you are using an EDL token instead of a launchpad or echo
headers = {"Authorization": f"{token}"}
cursor = ""
page_num = 0
query = """query ($params: CollectionsInput) {
  collections(params: $params) {
    cursor
    items {
      conceptId
    }
  }
}"""

variables = """{
  "params":{
    "limit":1,
    "cursor":"%s"
  }
}"""% (cursor)

response = requests.post(url=endpoint, json={"query": query, "variables": variables}, headers=headers, timeout=5)
first_result = response.json()

# Retrieve the first cursor value
if (response.status_code == 200):
  cursor = first_result.get('data', {}).get('collections', {}).get('cursor')
else:
  print("There was a failure in retrieving the first cursor check logs for status code")
  logging.debug('Response status code:  f{response.status_code}')
  sys.exit()

# Retrieve subsequent collections
if response.status_code == 200:
    all_collections = []
    while(cursor):
        # update variable by passing in the cursor with the updated value
        variables = """{
        "params":{
            "limit":1000,
            "cursor":"%s"
        }
        }"""% (cursor)
        print('current page', page_num)
        logging.debug('Search_after cursor values f{cursor}')
        response = requests.post(url=endpoint, json={"query": query, "variables": variables}, headers=headers, timeout=5)
        result = response.json()
        collections = result.get('data', {}).get('collections', {}).get('items', [])
        cursor = result.get('data', {}).get('collections', {}).get('cursor')
        logging.debug('Response in json: f{collections}')
        for collection in collections:
            all_collections.append(collection.get('conceptId'))
        page_num = page_num + 1
  
    print('Total number of pages f{page_num}')
    all_collections.sort()
    # Write the sorted concept-id list to a local folder
    with open("collectionConceptIdList.txt", "w", encoding='UTF-8') as txt_file:
        for collection in all_collections:
            txt_file.write(f"{collection}\n")