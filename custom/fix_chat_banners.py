import os
import glob

from zep.zendesk import KB
from zep.helpers import read_from_json, get_page_markup, create_tree, get_id_from_filename, write_to_json


kb = KB('chat')

locales = 'en-us', 'de', 'es', 'fr', 'ja', 'pt-br'
for locale in locales:
    folder = os.path.join('chat_banners', locale)
    kb.push_staged(folder, locale=locale, write=True)


 # # Download all articles in inventory for each locale
# locales = 'en-us', 'de', 'es', 'fr', 'ja', 'pt-br'
# for locale in locales:
#     file_path = os.path.join(kb.staging, 'chat_banners', locale)
#     inventory = f'kb_{locale}_article_inventory.json'
#     articles = read_from_json(os.path.join('cache', 'chat', inventory))
#     for article in articles:
#         translation = kb.get_translation(article['id'], locale)
#         markup = get_page_markup(translation)
#         filename = '{}.html'.format(translation['source_id'])
#         with open(os.path.join(file_path, filename), mode='w', encoding='utf-8') as f:
#             f.write(markup)
#         print('{} written'.format(filename))

# # Go thru en-us articles and build a banner map = {id: filename}
# banner_map = {}
# file_path = os.path.join(kb.staging, 'chat_banners', 'en-us')
# ignore_dev = read_from_json(os.path.join(file_path, 'ignore_dev.json'))
#
# files = glob.glob(os.path.join(file_path, '*.html'))
# for file in files:
#     article_id = get_id_from_filename(file)
#     if article_id in ignore_dev:
#         continue
#     tree = create_tree(file)
#     images = tree.find_all('img')
#     for image in images:
#         src = image['src']
#         if 'plan_available_chat_' in src:
#             banner_map[article_id] = src
#             break
#     if article_id not in banner_map:
#         banner_map[article_id] = None
#
# write_to_json(banner_map, file_path, 'banner_map.json')
# for mapping in banner_map:
#     print(f'{mapping}: {banner_map[mapping]}')

# # Get ignore article ids
# ignore_dev = []
# en_articles = read_from_json(os.path.join('cache', 'chat', 'kb_en-us_article_inventory.json'))
# for article in en_articles:
#     if article['section_id'] in [202527497, 202544568]:
#         ignore_dev.append(article['id'])
# write_to_json(ignore_dev, file_path, 'ignore_dev.json')

# on upload, ignore all articles with section_id in [202527497, 202544568]. Developers articles have wrong Talk banners
        # in English. No changes.


# # map en-us banners to loc articles
# locales = 'de', 'es', 'fr', 'ja', 'pt-br'
# banner_map = read_from_json(os.path.join(kb.staging, 'chat_banners', 'en-us', 'banner_map.json'))
# ignore_dev = read_from_json(os.path.join(kb.staging, 'chat_banners', 'en-us', 'ignore_dev.json'))
#
# for locale in locales:
#     print(f'\nLocale: {locale}\n')
#     file_path = os.path.join(kb.staging, 'chat_banners', locale)
#     files = glob.glob(os.path.join(file_path, '*.html'))
#     if locale is 'pt-br':
#         token = 'pt'
#     else:
#         token = locale
#     for file in files:
#         article_id = get_id_from_filename(file)
#         if article_id in ignore_dev:
#             print(f'{article_id}: Developers article')
#             continue
#         if str(article_id) not in banner_map:
#             print(f'{article_id}: No en-us source')
#             continue
#         if banner_map[str(article_id)] is None:
#             print(f'{article_id}: No banner in en-us source')
#             continue
#         tree = create_tree(file)
#         images = tree.find_all('img')
#         for image in images:
#             src = image['src']
#             if 'plan_available_chat_' in src:
#                 banner_src = banner_map[str(article_id)]
#                 banner_src = banner_src.replace('docs/en', f'docs/{token}')
#                 if src != banner_src:
#                     print(f'{article_id}: Mismatch with en src')
#                     print(f'     - {banner_src}')
#                     print(f'     - {src}')
#             break
