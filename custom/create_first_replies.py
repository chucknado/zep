import json
from urllib.parse import urlencode
from random import sample, choice

import requests

"""
This script searches for all tickets in falcon with a status of new. It then replies to a percentage of them.
You can adjust the 'percent' variable.
Required: Python 3 or higher and the requests library (http://docs.python-requests.org/en/master/).
For setup steps, see the API quick start at https://help.zendesk.com/hc/en-us/articles/229136887
"""

# Settings
root = 'https://falcon-support.zendesk.com'
endpoint = '/api/v2/search.json'
params = {'query': 'type:ticket status:new'}
url = root + endpoint + '?' + urlencode(params)
access_token = '34bfe80083c1859b1394ce583e804a5ac7c4faa8797b901c84012a1cfdf633f2'
headers = {'Authorization': 'Bearer ' + access_token}

# Get tickets with status of new
new_tickets = []
while url:
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print('Status:', response.status_code, 'Problem with the request. Exiting.')
        exit()
    data = response.json()
    new_tickets.extend((data['results']))
    url = data['next_page']

# Create replies
percent = 0.8    # percentage of new tickets to reply to
tickets = sample(new_tickets, int(percent*len(new_tickets)))
agents = [10468498945, 10468519025, 10468527665, 10468531965, 10507733629, 10507740449]
for ticket in tickets:
    assigned_agent = choice(agents)  # assigned to a random agent
    reply = {'ticket': {'comment': {'body': 'Gone fishing.', 'author_id': assigned_agent}}}
    endpoint = '/api/v2/tickets/{}.json'.format(ticket['id'])
    url = root + endpoint
    payload = json.dumps(reply)
    # response = requests.put(url, data=payload, headers=headers)
    # if response.status_code != 200:
    #     print('Status:', response.status_code, 'Problem with the request. Exiting.')
    #     exit()
    print('Replied to ticket {}'.format(ticket['id']))
