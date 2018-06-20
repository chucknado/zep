import os
import glob
import time
import shutil
from urllib.parse import urlencode

import arrow
from zep.zendesk import HelpCenter
from zep.zendesk import KB
from zep.helpers import write_to_json, read_from_json, get_page_markup


def get_edited_articles():
    products = ['help', 'explore', 'chat', 'support']
    product_totals = {}
    for product in products:
        total = 0
        edited = 0
        kb = KB(product)
        articles = read_from_json(os.path.join(kb.product_cache, kb.product_inventory))
        for article in articles:
            total += 1
            if '2017' in article['edited_at']:
                edited += 1
        product_totals[product] = [edited, total]
    return product_totals


def search_articles(qs, hc):
    kb = KB(hc)
    params = {'query': qs}
    url = kb.kb_root + '/articles/search.json?' + urlencode(params)
    response = kb.session.get(url)
    if response.status_code == 429:
        print('Rate limited! Please wait.')
        time.sleep(int(response.headers['retry-after']))
        response = kb.session.get(url)
    if response.status_code != 200:
        print('Error with status code {}'.format(response.status_code))
        exit()
    data = response.json()
    for result in data['results']:
        print((result['title']))
        print('https://support.zendesk.com/hc/en-us/articles/{}\n'.format(result['id']))

# --- Download and delete articles from HC ---

# # in run.py
# from zep.maintenance import get_archive_inventory, download_archive_articles, delete_archive_articles
# section_list = [200625566, 200625586]
# criteria = {'last_update_older_than_months': 12}
# get_archive_inventory('2017-06-30', 'support', section_list, criteria=criteria)
# download_archive_articles('2017-06-30', hc='support')
#
# delete_archive_articles('2017-06-30', hc='support', confirm=True)
#
# or
#
# section_map = {200625586: 203227478, 200625566: 203222478}
# move_archive_articles('2017-06-30', section_map, hc='support', confirm=True)


def get_archive_inventory(archive_name, hc, section_list, criteria=None):
    """
    Create inventory of all articles in the specified sections.
    :param archive_name: Name for archive folder
    :param hc: One of 'support', 'chat', 'help', 'bime', or 'explore'
    :param section_list: List of section ids
    :param criteria: Dict of criteria for article to be included in the archive. See
    check_article_meets_archive_criteria() docs for spec.
    :return: Nothing
    """
    file_path = os.path.join('..', 'backups', archive_name)
    if os.path.exists(file_path):
        print(f'An archive folder named {archive_name} already exists. Exiting.')
        exit()
    os.makedirs(file_path)

    kb = KB(hc)
    locales = ['en-us', 'de', 'es', 'fr', 'ja', 'pt-br']
    articles = {}
    sections = []
    for section_id in section_list:
        # create article inventory
        section_articles = []  # list of id/title/author/section_id/url dicts
        for locale in locales:
            url = kb.kb_root + f'/{locale}/sections/{section_id}/articles.json?include=users'
            article_list = kb.get_record_list(url)
            user_names = {}
            for user in article_list['users']:
                if user['id'] not in user_names:
                    user_names[user['id']] = user['name']

            for article in article_list['articles']:
                print('Reading {}'.format(article['id']))
                if criteria is not None:
                    if check_article_meets_archive_criteria(article, criteria) is False:
                        continue
                section_articles.append({'id': article['id'], 'title': article['title'],
                                         'author': user_names[article['author_id']], 'section_id': section_id,
                                         'locale': article['locale'], 'source_locale': article['source_locale'],
                                         'created_at': article['created_at'], 'updated_at': article['updated_at'],
                                         'url': article['html_url']})

        articles[section_id] = section_articles

        # create section inventory
        url = kb.kb_root + f'/en-us/sections/{section_id}.json'
        section = kb.get_record(url)
        sections.append(section)

    # Write files in production/backups
    write_to_json(articles, file_path, 'article_inventory.json')
    write_to_json(sections, file_path, 'section_list.json')
    print(f'Inventory for archive {archive_name} written')


def check_article_meets_archive_criteria(article, criteria):
    """
    Exclude article from archive if any test fails
    :param article: Article object
    :param criteria: A dict of criteria to meet to be included in the archive
        criteria = {
            'has_label': 'test_lbl',
            'does_not_have_label': 'do_not_archive',
            'older_than_months': 12,
            'last_update_older_than_months': 12
            'created_before_date': '2017-03-15'
        }
    :return: False if any criteria is not met; True if all criteria are met
    """

    if 'has_label' in criteria:
        labels = article['label_names']
        if criteria['has_label'] not in labels:
            return False

    if 'does_not_have_label' in criteria:
        labels = article['label_names']
        if criteria['does_not_have_label'] in labels:
            return False

    if 'is_not_article' in criteria:
        article_id = article['id']
        if article_id in criteria['is_not_article']:
            return False

    if 'older_than_months' in criteria:
        now = arrow.utcnow()
        cutoff_date = now.replace(months=-criteria['older_than_months'])
        created_at = arrow.get(article['created_at'])
        if created_at > cutoff_date:
            return False

    if 'last_update_older_than_months' in criteria:
        now = arrow.utcnow()
        cutoff_date = now.replace(months=-criteria['last_update_older_than_months'])
        updated_at = arrow.get(article['updated_at'])
        if updated_at > cutoff_date:
            return False

    if 'created_before_date' in criteria:
        cutoff_date = arrow.get(criteria['created_before_date'])
        created_at = arrow.get(article['created_at'])
        if created_at > cutoff_date:
            return False

    else:
        return True


def download_archive_articles(archive_name, hc):
    """
    Write all articles in the article_inventory.json file in the named backups folder on disk. Creates sections folders 
    for the files.
    :param archive_name: Folder that contains the article_inventory.json file
    :param hc: 'support', 'chat', 'help', 'explore', or 'bime'
    :return: 
    """
    path = os.path.join('..', 'backups', archive_name)
    if not os.path.exists(path):
        print(f'No folder named {archive_name} exists. Exiting.')
        exit()

    kb = KB(hc)
    file_path = os.path.join(path, 'article_inventory.json')
    inventory = read_from_json(file_path)

    for section in inventory:
        write_path = os.path.join(path, str(section))
        if os.path.exists(write_path):
            print(f'Section folder named already exists. Exiting.')
            exit()
        os.makedirs(write_path)
        for article in inventory[section]:
            translation = kb.get_translation(article['id'], article['locale'])
            if translation is None:
                print('{} translation is None'.format(article['id']))
                continue
            markup = get_page_markup(translation)
            if markup is None:
                print('{} markup is None'.format(article['id']))
                continue
            filename = '{}_{}.html'.format(article['id'], article['locale'])
            with open(os.path.join(write_path, filename), mode='w', encoding='utf-8') as f:
                f.write(markup)
            print('{} written'.format(filename))


def delete_archive_articles(archive_name, hc='support', confirm=False):
    """
    Delete all articles in the article_inventory.json file.
    :param archive_name: Folder that contains the article_inventory.json file 
    :param confirm: Force user to include confirm=True to actually delete the section
    :param hc: 'support', 'chat', 'help', 'explore', or 'bime'
    :return: 
    """
    if confirm is False:
        print(f'Are you sure you want to delete the articles?')
        print('If yes, rerun with confirm=True')
        exit()

    path = os.path.join('..', 'backups', archive_name)
    if not os.path.exists(path):
        print(f'No folder named {archive_name} exists. Exiting.')
        exit()

    kb = KB(hc)
    file_path = os.path.join(path, 'article_inventory.json')
    inventory = read_from_json(file_path)
    for section in inventory:
        for article in inventory[section]:
            if article['locale'] != article['source_locale']:   # delete only if it's the default locale of the article
                print(f"Skipping {article['id']}. Locale is {article['locale']} "
                      f"but source locale {article['source_locale']}")
                continue
            print(f"Deleting {article['id']} in locale {article['locale']}")
            endpoint = '/articles/{}.json'.format(article['id'])
            url = kb.kb_root + endpoint
            kb.delete_record(url)


# This is not tested completely yet
def move_archive_articles(archive_name, section_map, hc='support', confirm=False):
    """
    Delete all articles in the article_inventory.json file.
    :param archive_name: Folder that contains the article_inventory.json file
    :param section_map: A dict of source and destination section ids. Example {200625566: 200421969}
    :param confirm: Force user to include confirm=True to actually delete the section
    :param hc: 'support', 'chat', 'help', 'explore', or 'bime'
    :return:
    """
    if confirm is False:
        print(f'Are you sure you want to move the articles?')
        print('If yes, rerun with confirm=True')
        exit()

    path = os.path.join('..', 'backups', archive_name)
    if not os.path.exists(path):
        print(f'No folder named {archive_name} exists. Exiting.')
        exit()

    kb = KB(hc)
    file_path = os.path.join(path, 'article_inventory.json')
    inventory = read_from_json(file_path)
    for section in inventory:
        if int(section) not in section_map:
            print(f'Error. Archive source section id {section} not in section map.')
            continue
        for article in inventory[section]:
            if article['locale'] != article['source_locale']:   # move only if it's the default locale of the article
                print(f"Skipping {article['id']}. Locale is {article['locale']} "
                      f"but source locale {article['source_locale']}")
                continue
            print(f"Moving {article['id']} in locale {article['locale']}")
            payload = {'article': {'section_id': section_map[int(section)]}}
            url = kb.kb_root + '/articles/{}.json'.format(article['id'])
            # response = kb.put_record(url, payload)
            if True:
            # if response == 200:
                print('Moved article {}, {}'.format(article['id'], article['title']))


# --- Annual loc refresh --- #

def create_loc_refresh_loader(hc, last_refresh):
    """
    1. Gets all en-us articles that have translations
    2. Gets articles in the results that have a en-us translation that was updated after the start date
    3. Gets articles in the results that have a en-us translation that was updated after being handed off
    In run.py:
    > from zep.maintenance import create_loc_refresh_loader
    > create_loc_refresh_loader('support', last_refresh='2016-11-18')

    Run the function once for each HC. Use the loader file to prepare the loc handoff files for each HC using the
    normal loc handoff process (https://github.com/chucknado/zep/blob/master/docs/localizing_articles.md).

    To get specific categories in each HC, temporarily modify the category lists in the
    tools.ini file. Example to get articles only from the Admin category:

    ;support_categories=200201826,200201976,204155808,204155828
    support_categories=200201826

    :param hc: Help Center subdomain
    :param last_refresh: When the period of updates starts. Usually the date of the previous year's refresh handoff
    :return: Nothing. '{now.year}_loc_refresh_loader.txt`' is created in the product cache folder
    """
    loader = ''
    start_date = arrow.get(last_refresh).shift(days=1)   # updates start 1 day after date of last refresh handoff
    current_year = arrow.now().year

    kb = KB(hc)

    print('Taking kb article inventory...')
    kb.take_inventory()

    print('Keeping only the English articles that were localized...')
    kb.take_localized_article_inventory()

    print('Keeping only the English articles that we updated after the start date...')
    localized_articles = read_from_json(os.path.join(kb.product_cache, 'kb_localized_article_inventory.json'))
    updated_articles = []
    for article in localized_articles:
        print('Checking when {} was last updated...'.format(article['id']))
        translation = kb.get_translation(article['id'], 'en-us')
        updated_at = arrow.get(translation['updated_at'])
        if updated_at < start_date:
            continue
        article['en-us_updated_at'] = translation['updated_at']
        updated_articles.append(article)
    fname = f'{current_year}_loc_refresh_updated_articles.json'
    write_to_json(updated_articles, kb.product_cache, fname)
    print(f'{fname} saved to cache.')

    print('Keeping only the English articles that we updated after we handed them off...')
    articles = read_from_json(os.path.join(kb.product_cache, f'{current_year}_loc_refresh_updated_articles.json'))
    handoffs = read_from_json(os.path.join(kb.shared_folder, 'handoff_log.json'))
    # localized_at = start_date.shift(years=-1)  # make sure it's before the start date

    for article in articles:
        article_id = article['id']
        article_updated_at = arrow.get(article['en-us_updated_at'])
        article_localized = False
        print(f'\nChecking article {article_id}, updated on {article_updated_at}')

        for handoff in handoffs[hc]:
            if arrow.get(handoff['date']) < arrow.get(last_refresh):        # skip older handoffs
                print('Skipping older handoff {}'.format(handoff['date']))
                continue
            if article_id in handoff['files']:
                print('Handed off on {}'.format(handoff['date']))
                localized_at = arrow.get(handoff['date']).shift(days=1)
                if article_updated_at < localized_at:   # if last updated before the handoff
                    article_localized = True
                    break                               # last updated before an handoff - exit handoff loop

        if article_localized is False:
            print('Adding to loader...')
            if loader == '':
                loader += str(article_id)
            else:
                loader += '\n' + str(article_id)

    file = os.path.join(kb.product_cache, f'{current_year}_loc_refresh_loader.txt')
    with open(file, mode='w', encoding='utf-8') as f:
        f.write(loader)
    print('\nLoc refresh loader saved to cache.')


# ----------------- #
# Utility functions #
# ----------------- #

def get_new_articles_2017():
    products = ['support', 'chat', 'explore']
    for product in products:
        new_articles = []
        kb = KB(product)
        articles = read_from_json(os.path.join(kb.product_cache, kb.product_inventory))
        for article in articles:
            if '2017-' in article['created_at']:
                new_articles.append(article)
        write_to_json(new_articles, kb.product_cache, f'new_articles_{product}.json')