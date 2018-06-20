import os
import glob
import re

from lxml import etree


parser = etree.XMLParser(recover=True)
folders = ['admin_guide', 'admin_guide_enterprise', 'admin_guide_support_cookbook', 'agent_guide',
           'getting_started_current_gsg']
# folders = ['admin_guide']

new_path = 'http://zen-marketing-documentation.s3.amazonaws.com/docs/en/'
patterns = [
    'http://cdn.zendesk.com/images/documentation/admin_guide/help_center/',
    'http://cdn.zendesk.com/images/documentation/admin_guide/enterprise/',
    'http://cdn.zendesk.com/images/documentation/admin_guide/support_cookbook/',
    'http://cdn.zendesk.com/images/documentation/admin_guide/',
    'http://cdn.zendesk.com/images/documentation/gsg_ent/',
    'http://cdn.zendesk.com/images/documentation/gsg/',
    'http://cdn.zendesk.com/images/documentation/agent_guide/',
    'http://cdn.zendesk.com/images/documentation/apps/',
    'http://cdn.zendesk.com/images/documentation/optimizing/',
    'http://cdn.zendesk.com/images/documentation/'
]

for folder in folders:
    files = glob.glob(os.path.join('..', 'current_dita', folder, '*.dita'))
    # files = ['../current_dita/admin_guide/zug_voice.dita']

    print('\nFOLDER: {}\n'.format(folder))
    path_len = 16 + len(folder) + 1
    for file in files:
        modified = False
        if file[path_len:] == 'voice_pricing.dita': continue        # don't check this file
        with open(file, mode='rb') as f:
            tree = etree.parse(f, parser)                           # returns an ElementTree
        for image in tree.iter('image'):
            href = image.attrib['href']
            for pattern in patterns:
                if pattern in href:
                    image.attrib['href'] = re.sub(pattern, new_path, image.attrib['href'])
                    modified = True
                    print('  Updated image - {}'.format(image.attrib['href']))
                    break

        # print(etree.tostring(tree))
        if modified:
            print('Modified: {}'.format(file[path_len:]))
            tree.write(file, encoding='utf-8', xml_declaration=True)
            print('\n-----\n')
