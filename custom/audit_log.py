import os

from zep.zendesk import Zendesk
from zep.helpers import write_to_json

ticket_id = 123
zd = Zendesk('support')
url = os.path.join(zd.root, 'tickets', str(ticket_id), 'audits.json')
audit_log = zd.get_record_list(url)
write_to_json(audit_log, zd.product_cache, 'ticket_{}_audits.json'.format(ticket_id))
