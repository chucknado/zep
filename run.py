# from zep.zendesk import KB
# from zep.zendesk import HelpCenter
# from zep.zendesk import Core
# from zep.zendesk import Community
# from zep.zendesk import Support
# from zep.maintenance import get_filtered_post_list, move_posts
# from zep.maintenance import get_filtered_comment_list, delete_comments
from zep.archiver import get_filtered_article_list, move_articles
# from zep.maintenance import get_archive_inventory, download_archive_articles, delete_archive_articles,
# move_archive_articles
# from zep.workbench import Workbench
# from zep.maintenance import get_articles_with_translations, get_updated_since_start_date, get_updated_since_handoff, \
#     get_created_since_start_date
# from zep.maintenance import search_articles


get_filtered_article_list('support', section='announcements')
# move_articles('support', section='announcements', list_fname='announcements_archive_list_2018-01-29.json')

# from zep.maintenance import get_edited_articles
# results = get_edited_articles()
# print(results)

# from zep.maintenance import create_loc_refresh_loader
# create_loc_refresh_loader('support', last_refresh='2016-11-18')


# kb = KB('support')
# kb.take_inventory()

# get_articles_with_translations('explore')
# get_updated_since_start_date('chat', start_date='2016-11-18')  # 'support' is hc arg
# get_updated_since_handoff('chat')

# kb = KB('chat')
# kb.take_inventory(
# kb.take_localized_article_inventory()

# get_created_since_start_date('help', '2016-09-01')

# kb.backup_inventory('kb_fr_article_inventory.json', 'fr_updates', locale='fr')

# section_list = [200608963, 200625656, 200626376, 200623806, 200776597, 205910408, 201141038]
# criteria = {'last_update_older_than_months': 12}
# get_archive_inventory('2017-08-10', 'support', section_list)
# download_archive_articles('2017-08-10', hc='support')

# section_map = {200625586: 203227478, 200625566: 203222478}
# move_archive_articles('2017-06-30', section_map, hc='support', confirm=True)

# kb = KB('support')

# core = Core('support')
# core.list_user_events()
# users.show_me()

# wb = Workbench('Support')
# wb.move_unused_images(live_images='kb_image_inventory_2017-02-23_agent_guide.json')
# wb.get_used_source_images(live_images='kb_image_inventory_2017-02-23_voice.json')
# wb.copy_used_images('talk_used_source_images.json')
# wb.check_plan_banners()
# wb.get_no_banner_alt_text()

# get_filtered_comment_list()
# delete_comments()
# get_filtered_post_list()
# move_posts()

# get_filtered_article_list('support', section='announcements')
# move_articles('support', section='announcements', list_fname='announcements_archive_list_2017-05-08.json')

# kb = KB('support')
# kb.backup_inventory('kb_article_inventory.json', folder_name='2017-02-23_voice')
# kb.take_section_inventory(200625646, src_locale='en-us')
# kb.take_inventory()
# kb.take_inventory(categories=[204155828], drafts=True)
# kb.take_locale_inventory('ja')
# kb.take_localized_article_inventory()
# kb.take_image_inventory(backup_folder='2017-02-23_voice')


# url = 'https://support.zendesk.com/api/v2/apps.json'
# app_list = kb.get_record_list(url)
# for app in app_list['apps']:
#     print('App {}: {}'.format(app['id'], app['name']))

# hc = HelpCenter('help')
# followers = hc.list_followers(206223808, 'section')
# print(followers)

# tx = Support('support')
# tx.get_ticket_audit_log(2093423)

# kb.get_articles_by_docs_team()


# kb.add_dita_fname_to_inventory()
# kb.create_refresh_handoff_list()
# kb.get_files_to_remove()
# kb.get_files_to_add()

# kb.push_transformed_articles('2016-11-08')

# from zep.golion import Golion
# golion = Golion('support')
# golion.exclude_from_refresh_handoff()

# from zep.ditamap import Ditamap
# ditamap = Ditamap()
# ditamap.show()

# golion.find_links_dita_prob()
# golion.convert_to_yaml()
# golion.push_transformed_dita_articles('2016-11-08')
# golion.write_results_to_excel()


# kb = KB('support')
# kb.push_transformed_articles('support')

# from modules import Zendesk
#
# zd = Zendesk('zendesk')
# url = 'https://helptemp.zendesk.com/api/v2/help_center/en-us/sections/206223788.json'
# section = zd.get_record(url)
# print(section)

# inventory = kb.read_inventory()
# for article in inventory:
#     print(article)
# kb.take_ditaless_inventory()

# kb.push_staged('classic_eol', write=True)

# kb.update_dita_map(11111112, 'testfile')
# kb.archive_content(200623776)

# c.update_post(209947128, '206416167.html')


# image_registry = os.path.join('cache','zendesk', 'localized_images.p')
# with open(image_registry, mode='rb') as f:
#     registry = pickle.load(f)

# for locale in registry:
#     print(len(registry[locale]))

# from modules import Community
#
# c = Community('zendesk')
# c.create_post(2088390418, 200488257, title='Theming changes in the Support SDK', details='Coming soon')


# kb.archive_comments(203661816)


# sections = '203940048', '203948637'
# url = 'https://bimesupport.zendesk.com/api/v2/help_center/sections/203948637/articles.json?include=users'
# article_list = kb.get_record_list(url)

# for article in article_list:
#     print(article)


# article = kb.get_translation(218000607)
# print(article)

# kb.archive_content(200623806)


# kb.list_followers(200623826, 'section')

# hc = HelpCenter()
# hc.list_followers(200132086, 'topic')

# kb.debug_print()

# inventory = kb.read_inventory()
# for article in inventory:
#     print(article)


# kb = KB()
# kb.archive_content()

# inventory = kb.take_inventory([200201976])
# print(inventory)

# articles = kb.take_inventory([200201976])


# articles = kb.archive_content()
# for article in articles:
#     print(article)


# inventory = kb.read_inventory()
# for article in inventory:
#     print(article)

# dita_map = kb.read_dita_map()
# for article in dita_map:
#     print(str(article) + ': ' + dita_map[article])

# kb.update_dita_map(203663516, 'gsg_lesson5', change=True)
# for article in dita_map:
#     print(str(article) + ': ' + dita_map[article])

# 203663516,gsg_lesson5

# # Write registry
# registry_file = 'localized_images.p'
# with open(registry_file, mode='rb') as f:
#     registry = pickle.load(f)
# for locale in registry:
#     for item in registry[locale]:
#         print('{}: {}'.format(locale, item))


# dita_map = {234: 'filename1.dita', 235: 'filename2.dita', ... }

# locales = ['de', 'es', 'fr', 'ja', 'pt-br']


# registry = {}                   # initialize a new registry dict {'en': ['one.jpg', ... ], ... }
# for locale in locales:
#     registry[locale] = []
#
# for locale in locales:
#     image_files = ['one.jpg', 'two.png', 'three.png']
#     for image_file in image_files:
#         print('The {} image \'{}\' is not registered. Updating....'.format(locale, image_file))
#         registry[locale].append(image_file)
#
# print(registry)

# with open('localized_images_test.p', mode='wb') as f:
#     pickle.dump(registry, f)
#
# with open('localized_images_test.p', mode='rb') as f:
#     pickled_registry = pickle.load(f)
#
# print(pickled_registry)


# # arguments
# article_id = 236
# file_name = 'filename5.dita'
# change = False
# print_map = True
#
# if os.path.isfile('dita_map.p'):
#     with open('dita_map.p', mode='rb') as f:
#         dita_map = pickle.load(f)
# else:
#     dita_map = {}       # start new map
#
# if print_map:
#     for article in dita_map:
#         print('{}: {}'.format(article, dita_map[article]))
#     exit()
#
# if article_id in dita_map and change is False:
#     print('{} is already mapped to {}. To change this mapping, rerun the command with the --change option.'.format(
#           article_id, file_name))
#     exit()
#
# dita_map[article_id] = file_name
# with open('dita_map.p', mode='wb') as f:
#     pickle.dump(dita_map, f)
# print('Mapped article {} to {}.'.format(article_id, file_name))
