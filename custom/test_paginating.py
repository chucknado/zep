import requests


endpoint = '/api/v2/ticket_audits.json'
url = 'https://nadosolutions.zendesk.com' + endpoint

audits = []
while url:
    response = requests.get(url, auth=('chucknado@outlook.com', 'falcon63'))
    data = response.json()
    audits.extend(data['audits'])
    url = data['after_url']

for audit in audits:
    print(audit)


# # Get tickets with status of new
# new_tickets = []
# while url:
#     response = requests.get(url, headers=headers)
#     if response.status_code != 200:
#         print('Status:', response.status_code, 'Problem with the request. Exiting.')
#         exit()
#     data = response.json()
#     new_tickets.extend((data['results']))
#     url = data['next_page']
#
# # Create replies
# percent = 0.8    # percentage of new tickets to reply to
# tickets = sample(new_tickets, int(percent*len(new_tickets)))
# agents = [10468498945, 10468519025, 10468527665, 10468531965, 10507733629, 10507740449]
# for ticket in tickets:
#     assigned_agent = choice(agents)  # assigned to a random agent
#     reply = {'ticket': {'comment': {'body': 'Gone fishing.', 'author_id': assigned_agent}}}
#     endpoint = '/api/v2/tickets/{}.json'.format(ticket['id'])
#     url = root + endpoint
#     payload = json.dumps(reply)
#     response = requests.put(url, data=payload, headers=headers)
#     if response.status_code != 200:
#         print('Status:', response.status_code, 'Problem with the request. Exiting.')
#         exit()
#     print('Replied to ticket {}'.format(ticket['id']))
