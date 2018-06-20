import os
from urllib.parse import urlencode

from zep.zendesk import Zendesk
from zep.helpers import write_to_json

user_id = 295512778  # me
params = {
    'event_types[]': 'help_center.activity.events.ArticleViewed',
    'start_time': 1490054400
}

zd = Zendesk('support')
endpoint = os.path.join(zd.root, 'users', str(user_id), 'events')
url = endpoint + '?' + urlencode(params)
print(url)


event_list = zd.get_record_list(url)
write_to_json(event_list, zd.product_cache, f'user_{user_id}_events.json')
