import os
import glob

from zep.zendesk import KB
from zep.helpers import read_from_json, get_page_markup, create_tree, get_id_from_filename, write_to_json


kb = KB('support')
cat_id = 204155828

# # generate inventory of Talk articles
# kb.take_locale_inventory(locale='pt-br', categories=[cat_id])

# # Download all articles in inventory for each locale
# locales = 'en-us', 'de', 'es', 'fr', 'ja', 'pt-br'
# for locale in locales:
#     file_path = os.path.join(kb.staging, 'talk_banners', locale)
#     inventory = f'talk_{locale}_article_inventory.json'
#     articles = read_from_json(os.path.join('cache', 'support', inventory))
#     for article in articles:
#         translation = kb.get_translation(article['id'], locale)
#         markup = get_page_markup(translation)
#         filename = '{}.html'.format(translation['source_id'])
#         with open(os.path.join(file_path, filename), mode='w', encoding='utf-8') as f:
#             f.write(markup)
#         print('{} written'.format(filename))


# # Go thru en-us articles and build a banner map = {id: filename}
# banner_map = {}
# file_path = os.path.join(kb.staging, 'talk_banners', 'en-us')
#
# files = glob.glob(os.path.join(file_path, '*.html'))
# for file in files:
#     banners = []
#     article_id = get_id_from_filename(file)
#     if article_id == 203661526:  # talk pricing per country
#         continue
#     tree = create_tree(file)
#     images = tree.find_all('img')
#     for image in images:
#         src = image['src']
#         if 'plan_available_' in src:
#             banners.append(src)
#
#     if banners is not None:
#         banner_map[article_id] = banners
#
# write_to_json(banner_map, os.path.join(kb.staging, 'talk_banners'), 'banner_map.json')
# for mapping in banner_map:
#     print(f'{mapping}: {banner_map[mapping]}')

# # Add missing banners to loc articles
# banner_map = read_from_json(os.path.join(kb.staging, 'talk_banners', 'banner_map.json'))
# locales = 'de', 'es', 'fr', 'ja', 'pt-br'
# for locale in locales:
#     print(f'\n{locale}\n')
#     file_path = os.path.join(kb.staging, 'talk_banners', locale)
#     files = glob.glob(os.path.join(file_path, '*.html'))
#     for file in files:
#         mapping = []
#         article_id = str(get_id_from_filename(file))
#         print(f'Checking {article_id}')
#         if article_id == '203661526':
#             print(f'Skipping {article_id}')
#             continue
#
#         if banner_map[article_id]:
#             mapping = banner_map[article_id]
#         else:
#             continue
#
#         tree = create_tree(file)
#
#         # if article_id == '213857548':   # pre-test
#         #     print(tree.body)
#         #     print('\n\n')
#
#         # strip all banners
#         images = tree.find_all('img')
#         for image in images:
#             src = image['src']
#             if 'plan_available_' in src:
#                 image.decompose()
#         # strip head tag in body
#         if tree.find('head'):
#             tree.find('head').decompose()
#         # strip straggling meta tags
#         if tree.find('meta'):
#             meta_tags = tree.find_all('meta')
#             for tag in meta_tags:
#                 tag.decompose()
#         # strip h1 tag in body
#         if tree.find('h1'):
#             tree.find('h1').decompose()
#
#         for banner_url in reversed(mapping):
#             if locale == 'pt-br':
#                 token = 'pt'
#             else:
#                 token = locale
#             banner_url = banner_url.replace('docs/en', f'docs/{token}')
#             banner_tag = tree.new_tag("img", alt="plan banner", src=banner_url)
#             banner_tag['class'] = 'image'
#             nested_banner = tree.new_tag("p")
#             nested_banner.append(banner_tag)
#             tree.find("div", class_="body").insert(0, nested_banner)
#
#         print(f'Writing {article_id}')
#         with open(file, mode='w', encoding='utf-8') as f:
#             f.write(str(tree.body))
#
#         # if article_id == '213857548':   # post-test
#         #     print(tree.body)

# # push staged to hc
# locales = 'de', 'es', 'ja', 'pt-br'
# # locales = 'fr',
# for locale in locales:
#     print(f'\n{locale}\n')
#     file_path = os.path.join(kb.staging, 'talk_banners', locale)
#     files = glob.glob(os.path.join(file_path, '*.html'))
#     for file in files:
#         article_id = str(get_id_from_filename(file))
#         print(f'Putting translation {article_id}')
#         with open(file, mode='r', encoding='utf-8') as f:
#             body = f.read()
#         data = {'translation': {'body': body}}
#         kb.put_translation(article_id, locale, payload=data)
