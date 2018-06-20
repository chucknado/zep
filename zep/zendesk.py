import configparser
import os
import glob
import time
import json
from urllib.parse import urlparse, parse_qs

import yaml
import arrow
import requests

from YamJam import yamjam
from zep.ditamap import Ditamap
from zep.helpers import create_tree, get_id_from_filename, get_dita_name_from_filename, \
    write_to_excel, write_to_json, read_from_json, backup, get_page_markup


class Zendesk:
    def __init__(self, subdomain):
        self.subdomain = subdomain
        self.config = configparser.ConfigParser()
        self.config.read('tools.ini')
        self.settings = self.config['ZENDESK']
        self.product_cache = os.path.join('cache', self.subdomain)
        self.root = 'https://{}.zendesk.com/api/v2/'.format(self.subdomain)
        self.session = requests.Session()
        self.session.headers = {'Content-Type': 'application/json'}
        if 'user' in self.settings and 'api_token' in self.settings:
            self.session.auth = ('{}/token'.format(self.settings['user']), self.settings['api_token'])
        else:
            self.session.auth = ('{}/token'.format(yamjam()['ZEN_USER']), yamjam()['ZEN_API_TOKEN'])

    def get_record(self, url):
        """
        Runs a GET request on any Show endpoint in the Zendesk API
        :param url: A full endpoint url, such as 'https://support.zendesk.com/api/v2/help_center/articles/2342572.json'
        :return: If successful, a Python data structure mirroring the JSON response. If not, None
        """
        response = self.session.get(url)
        if response.status_code == 429:
            print('Rate limited! Please wait.')
            time.sleep(int(response.headers['retry-after']))
            response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print('Failed to get record with error {}'.format(response.status_code))
            return None

    def get_record_list(self, url):
        """
        Runs a GET request on any List endpoint in the Zendesk API
        :param url: A full endpoint url, such as 'https://support.zendesk.com/api/v2/help_center/articles.json'
        :return: A Python data structure mirroring the JSON response
        """

        o = urlparse(url)
        resource = os.path.splitext(os.path.basename(o.path))[0]
        record_list = {resource: []}
        has_sideload = False

        if o.query:
            query = parse_qs(o.query)       # query = {'include': ['users']}
            if 'include' in query:
                sideload = query['include'][0]
                if sideload not in ['access_policies']:     # any sideload without separate data structures
                    record_list = {resource: [], sideload: []}
                    has_sideload = True

        while url:
            response = self.session.get(url)
            if response.status_code == 429:
                print('Rate limited! Please wait.')
                time.sleep(int(response.headers['retry-after']))
                response = self.session.get(url)
            if response.status_code != 200:
                print('Error with status code {}'.format(response.status_code))
                exit()
            data = response.json()
            if data[resource]:                              # guard against empty record list
                record_list[resource].extend(data[resource])
                if has_sideload:
                    ids = []
                    [ids.append(record['id']) for record in record_list[resource]]
                    for record in data[sideload]:
                        if record['id'] in ids:
                            continue
                        record_list[sideload].append(record)
            url = data['next_page']
        return record_list

    def put_record(self, url, payload):
        """
        Runs a PUT request on any Update endpoint in the Zendesk API
        :param url: A full endpoint url, such 'https://support.zendesk.com/api/v2/help_center/articles.json'
        :param payload: Python data to update the record
        :return: If successful, a Python data structure mirroring the JSON response. If not, None
        """
        response = self.session.put(url, json=payload)
        if response.status_code == 429:
            print('Rate limited! Please wait.')
            time.sleep(int(response.headers['retry-after']))
            response = self.session.put(url, data=payload)
        if response.status_code == 200:
            return response.status_code
        else:
            print('Failed to update record with error {}'.format(response.status_code))
            print(response.reason)
            return None

    def post_record(self, url, payload, success_code=201):
        """
        Runs a PUT request on any Create endpoint in the Zendesk API
        :param url: A full endpoint url, such as 'https://support.zendesk.com/api/v2/help_center/articles.json'
        :param payload: Python data to update the record
        :param success_code: Most POST requests return 201, but some return 200
        :return: If successful, a Python data structure mirroring the JSON response. If not, None
        """
        response = self.session.post(url, json=payload)
        if response.status_code == 429:
            print('Rate limited! Please wait.')
            time.sleep(int(response.headers['retry-after']))
            response = self.session.post(url, data=payload)
        if response.status_code == success_code:
            return response.json()
        else:
            print('Failed to create record with error {}'.format(response.status_code))
            print(response.reason)
            return None

    def delete_record(self, url):
        """
        Runs a DELETE request on any Delete endpoint in the Zendesk API
        :param url: A full endpoint url, such as 'https://support.zendesk.com/api/v2/help_center/articles/2342572.json'
        :return: If successful, a 204 status code. If not, None
        """
        response = self.session.delete(url)
        if response.status_code == 429:
            print('Rate limited! Please wait.')
            time.sleep(int(response.headers['retry-after']))
            response = self.session.put(url)
        if response.status_code == 204:
            return response.status_code
        else:
            print('Failed to delete record with error {}'.format(response.status_code))
            return None


class HelpCenter(Zendesk):
    def __init__(self, product):
        Zendesk.__init__(self, product)
        self.kb_root = os.path.join(self.root, 'help_center')
        self.community_root = os.path.join(self.root, 'community')
        self.staging = os.path.join('..', 'staging')
        self.docs_team_cache = os.path.join('cache', 'docs_team')
        self.product_inventory = 'kb_article_inventory.json'

    def list_followers(self, content_id, content_type):
        """
        Prints a list of people who follow the specified the Help Center item
        :param content_id: ID of the Help Center item
        :param content_type: One of 'article', 'section', 'topic', 'post'
        :return: nothing
        """
        if content_type == 'topic' or content_type == 'post':
            root = self.community_root
        else:
            root = self.kb_root
        url = root + '/{}/{}/subscriptions.json?include=users'.format(content_type + 's', content_id)
        subscription_list = self.get_record_list(url)
        followers = []
        for sub in subscription_list['subscriptions']:
            for user in subscription_list['users']:
                if user['id'] == sub['user_id']:
                    followers.append(user['name'])
                    break
        if len(followers) < 1:
            follower_string = 'no followers.'
        elif len(followers) is 1:
            follower_string = '1 follower'
        else:
            follower_string = '{} followers:'.format(len(followers))
        print('This {} has {}'.format(content_type, follower_string))
        if followers:
            for follower in followers:
                print(follower)

    def list_votes(self, content_id, content_type):
        """
        Prints a list of votes on the specified the Help Center item
        :param content_id: ID of the Help Center item
        :param content_type: One of 'article' or 'post'
        :return: nothing
        """
        if content_type == 'post':
            root = self.community_root
        else:
            root = self.kb_root
        url = root + '/{}/{}/votes.json?include=users'.format(content_type + 's', content_id)
        vote_list = self.get_record_list(url)
        votes = []
        thumbs = {1: 'Thumbs up', -1: 'Thumbs down'}
        for vote in vote_list['votes']:
            for user in vote_list['users']:
                if user['id'] == vote['user_id']:
                    result = '{} from {} ({})'.format(thumbs[vote['value']], user['name'], vote['user_id'])
                    votes.append(result)
                    break
        if len(votes) < 1:
            vote_string = 'no votes.'
        elif len(votes) is 1:
            vote_string = '1 vote'
        else:
            vote_string = '{} votes:'.format(len(votes))
        print('This {} has {}'.format(content_type, vote_string))
        if votes:
            for vote in votes:
                print(vote)


class Community(HelpCenter):

    def __init__(self, product):
        HelpCenter.__init__(self, product)

    def get_posts_in_topic(self, topic):
        endpoint = '/topics/{}/posts.json'.format(topic)
        url = self.community_root + endpoint
        response = self.get_record_list(url)
        if response:
            return response['posts']   # list of dicts

    def get_post(self, post_id):
        endpoint = '/posts/{}.json'.format(post_id)
        url = self.community_root + endpoint
        response = self.get_record(url)
        if response:
            return response['post']   # post dict

    def create_post_in_drafts(self, author_id):
        endpoint = '/posts.json'
        url = self.community_root + endpoint
        draft_topic = {'support': 200133376, 'chat': 200661807, 'bime': 200674538}
        topic_id = draft_topic[self.subdomain]
        title = 'Placeholder post'
        details = 'Coming soon'
        data = {'post': {'author_id': author_id, 'topic_id': topic_id, 'title': title, 'details': details}}
        response = self.post_record(url, payload=data)
        if response:
            print('Successfully created post {}'.format(response['post']['id']))

    def update_post_from_file(self, post_id, filename):
        endpoint = '/posts/{}.json'.format(post_id)
        url = self.community_root + endpoint
        file = os.path.join(self.staging, 'posts', filename)
        tree = create_tree(file)
        if tree.h1.string is None:
            print('ERROR: title h1 problem in {} (extra inner tags, etc)'.format(filename))
            exit()
        title = tree.h1.string.strip()
        tree.h1.decompose()
        data = {'post': {'title': title, 'details': str(tree)}}
        response = self.put_record(url, payload=data)
        if response:
            print('Successfully updated post {}'.format(post_id))


class KB(HelpCenter):

    def __init__(self, product):
        HelpCenter.__init__(self, product)
        self.settings = self.config['KB']
        self.shared_folder = os.path.join(os.sep, *self.settings['shared_folder'].split('/'))
        self.dita_map = os.path.join(self.shared_folder, 'ditamap.yml')
        categories = self.settings[product + '_categories']
        if categories == '':                        # no category specified in ini file
            self.categories = []
        elif len(categories) == 1:
            self.categories = [categories]
        else:
            self.categories = categories.split(',')

    def get_translation(self, article, locale='en-us'):
        """
        Get a translation of an article
        :param article: The id of the source article
        :param locale: The locale code of the translation
        :return: If successful, a translation dict structured per the Translations API doc. If not, None
        """
        endpoint = '/articles/{}/translations/{}.json'.format(article, locale)
        url = self.kb_root + endpoint
        response = self.get_record(url)
        if response:
            response = response['translation']
        return response

    def get_missing_translations(self, article):
        """
        Get missing translations for an article, to know when to POST and when to PUT on upload
        :param article: The id of the source article
        :return: If successful, a list of locale codes such as ["de", "es", ...]. If not, None.
        """
        url = self.kb_root + '/articles/{}/translations/missing.json'.format(article)
        response = self.get_record(url)
        if response:
            response = response['locales']
        return response

    def put_translation(self, article, locale, payload):
        """
        Update a translation
        :param article: The id of the source article
        :param locale: The locale code of the translation
        :param payload: A translation JSON object structured per the Update Translation doc
        :return: Nothing
        """
        if locale == 'ptbr' or locale == 'pt':
            locale = 'pt-br'
        url = self.kb_root + '/articles/{}/translations/{}.json'.format(article, locale)
        response = self.put_record(url, payload=payload)
        if response:
            print('Successfully updated {} translation of article {}'.format(locale, article))
        else:
            print('Error updating {} translation of article {}'.format(locale, article))

    def post_translation(self, article, payload):
        """
        Create a translation (the payload specifies the locale)
        :param article: The id of the source article
        :param payload: A translation JSON object structured per the Create Translation doc
        :return: Nothing
        """
        url = self.kb_root + '/articles/{}/translations.json'.format(article)
        response = self.post_record(url, payload=payload)
        if response:
            print('Successfully created translation of article {}'.format(article))
        else:
            print('Error creating translation of article {}'.format(article))

    def push_staged(self, folder, locale='en-us', write=False):
        """
        Pushes id-named html files in staging folder specified in tools.ini
        :param folder: Folder in the staging folder containing the files
        :param locale: Default
        :param write: Actually put the files.
        :return:
        """
        path = os.path.join(os.sep, *self.settings['staging'].split('/'), folder)
        if not os.path.exists(path):
            print('Folder named "{}" not found in the staging folder.'.format(folder))
            exit()
        files = glob.glob(os.path.join(path, '*.html'))
        for file in files:
            article_id = get_id_from_filename(file)
            if article_id == 203661746:
                print('Glossary, 203661746, skipped. Enter manually.')
                continue

            missing_translations = self.get_missing_translations(article_id)
            if missing_translations is None:
                print('Error getting missing translations for article {}. Exiting'.format(article_id))
                exit()
            if locale in missing_translations:  # get http method to use for article
                http_method = 'post'
            else:
                http_method = 'put'

            tree = create_tree(file)
            title = ' '.join(tree.h1.stripped_strings)
            tree.h1.decompose()

            if http_method == 'post':
                data = {'translation': {'locale': locale, 'title': title, 'body': str(tree.body), 'draft': False}}
                if write:
                    print(f'Posting translation {article_id}: {title}')
                    self.post_translation(article_id, payload=data)
            else:
                data = {'translation': {'title': title, 'body': str(tree), 'draft': False}}
                if write:
                    print(f'Putting translation {article_id}: {title}')
                    self.put_translation(article_id, locale, payload=data)

    def push_transformed_articles(self, folder, write=True):
        """
        Pushes dita-transformed html files to the appropriate KBs.
        Reads the ditamap.yml file in the /production folder on the Documentation Team Drive.
        Looks for the transformed files in the production/staging/transformed_files folder.
        :param folder: The name of folder in /production/staging/transformed_files that contains the transformed files
        :param write: Boolean. If true, write changes to Help Centers
        :return: None, but prints the push results in json and xlsx files in /production/reports/publishing
        """
        with open(self.dita_map, 'r') as f:
            dita_map = yaml.load(f)
        files_path = os.path.join(os.sep, *self.settings['staging'].split('/'), 'transformed_files', folder)
        files = glob.glob(os.path.join(files_path, '*.html'))
        results = []
        for file in files:
            dita_name = get_dita_name_from_filename(file)
            mapping_exists = False
            for mapping in dita_map:
                if mapping['dita'] == dita_name:
                    mapping_exists = True
                    break
            if mapping_exists:
                print('Updating \"{}\" ({}) in {} kb'.format(mapping['dita'], mapping['id'], mapping['hc']))
                tree = create_tree(file)
                if tree.h1.string is None:
                    print('ERROR: title h1 problem in {} (extra inner tags, etc)'.format(mapping['dita']))
                    results.append(
                        {'dita': mapping['dita'], 'id': mapping['id'], 'hc': mapping['hc'], 'pushed': False,
                         'notes': 'h1 problem'})
                    continue
                title = tree.h1.string.strip()
                tree.h1.decompose()
                body = tree.body
                data = {'translation': {'title': title, 'body': str(body)}}
                hc_root = 'https://{}.zendesk.com/api/v2/help_center'.format(mapping['hc'])
                endpoint = '/articles/{}/translations/en-us.json'.format(mapping['id'])
                url = hc_root + endpoint
                print(url)
                if write:
                    response = self.put_record(url=url, payload=data)
                else:
                    print('Testing mode!')
                    response = 1
                if response is not None:
                    results.append(
                        {'dita': mapping['dita'], 'id': mapping['id'], 'hc': mapping['hc'], 'pushed': True,
                         'notes': ''})
                else:
                    results.append(
                        {'dita': mapping['dita'], 'id': mapping['id'], 'hc': mapping['hc'], 'pushed': False,
                         'notes': 'request error'})
            else:
                print('Skipping \"{}\" in {} kb because has no mapping'.format(mapping['dita'], mapping['hc']))
                results.append(
                    {'dita': dita_name, 'id': None, 'hc': None, 'pushed': False, 'notes': 'no mapping'})

            now = arrow.now('US/Pacific')
            report_name = 'push_results_{}'.format(now.format('YYYY-MM-DD'))

            reports_path = os.path.join(self.shared_folder, 'reports', self.subdomain, 'publishing')
            write_to_json(results, reports_path, '{}.json'.format(report_name))
            write_to_excel(results, reports_path, '{}.xlsx'.format(report_name))

    def take_inventory(self, categories=None, excel=False, drafts=False):
        """
        Gets a list of all articles in the specified categories in Help Center.
        Skips any section that's viewable only by agents and managers. Also skips any articles in Draft mode. Make
        sure to get a fresh version of the ditamap on the Documentation Team Drive (under /All products/production)
        :param categories: List of category ids. Omit argument for all categories
        :param excel: Whether to export the inventory to an Excel file or not
        :param drafts: Whether or not to include draft articles in the inventory
        :return: nothing
        """
        if categories is None:
            categories = self.categories
        dm = Ditamap()
        ditamap = dm.open()
        source_locale = 'en-us'
        kb_articles = []  # list of id/title/author/section_id/url dicts
        for category in categories:
            url = self.kb_root + f'/{source_locale}/categories/{category}/sections.json'
            section_list = self.get_record_list(url)
            for section in section_list['sections']:
                if section['locale'] != source_locale:
                    continue
                if section['user_segment_id']:
                    url = self.kb_root + '/user_segments/{}.json'.format(section['user_segment_id'])
                    user_segment = self.get_record(url)['user_segment']
                    if user_segment['user_type'] == 'staff':
                        continue

                url = self.kb_root + f'/{source_locale}/sections/{section["id"]}/articles.json?include=users'
                article_list = self.get_record_list(url)
                user_names = {}
                for user in article_list['users']:
                    if user['id'] not in user_names:
                        user_names[user['id']] = user['name']

                for article in article_list['articles']:
                    if article['source_locale'] != source_locale:
                        continue
                    if drafts is False and article['draft']:
                        continue

                    dita_name = None
                    for mapping in ditamap:
                        if mapping['id'] == article['id']:
                            dita_name = mapping['dita']
                            break

                    kb_articles.append({'id': article['id'], 'title': article['title'], 'dita': dita_name,
                                        'author': user_names[article['author_id']], 'section_id': article['section_id'],
                                        'created_at': article['created_at'], 'edited_at': article['edited_at'],
                                        'source_locale': article['source_locale'],
                                        'url': article['html_url']})
        write_to_json(kb_articles, self.product_cache, self.product_inventory)
        print('Inventory written to {}'.format(os.path.join(self.product_cache, self.product_inventory)))
        if excel is True:
            fname = self.product_inventory[:-4] + 'xlsx'
            write_to_excel(kb_articles, self.product_cache, fname)
            print('Inventory of {} articles written to Excel in {}'.format(len(kb_articles), self.product_cache))

    def take_locale_inventory(self, locale='en-us', categories=None):
        """
        Gets a list of all articles in the specified locale and categories in Help Center.
        Skips any section that's viewable only by agents and managers. Also skips any articles in Draft mode.
        :param locale: The locale of the articles
        :param categories: List of category ids. Omit argument for all categories
        :return: nothing
        """
        if categories is None:
            categories = self.categories
        kb_articles = []  # list of id/title/author/section_id/url dicts
        for category in categories:
            url = self.kb_root + '/{}/categories/{}/sections.json'.format(locale, category)
            section_list = self.get_record_list(url)
            for section in section_list['sections']:
                if section['user_segment_id']:
                    url = self.kb_root + '/user_segments/{}.json'.format(section['user_segment_id'])
                    user_segment = self.get_record(url)['user_segment']
                    if user_segment['user_type'] == 'staff':
                        continue
                url = self.kb_root + '/{}/sections/{}/articles.json?include=users'.format(locale, section['id'])
                article_list = self.get_record_list(url)
                user_names = {}
                for user in article_list['users']:
                    if user['id'] not in user_names:
                        user_names[user['id']] = user['name']

                for article in article_list['articles']:
                    if article['draft']:
                        continue
                    kb_articles.append({'id': article['id'], 'title': article['title'],
                                        'author': user_names[article['author_id']], 'section_id': article['section_id'],
                                        'source_locale': article['source_locale'], 'created_at': article['created_at'],
                                        'url': article['html_url']})
        fname = f'kb_{locale}_article_inventory.json'
        write_to_json(kb_articles, self.product_cache, fname)
        print('Inventory written to {}'.format(os.path.join(self.product_cache, self.product_inventory)))

    def take_section_inventory(self, section_id, src_locale='en-us'):
        dm = Ditamap()
        ditamap = dm.open()
        section_articles = []         # list of id/title/author/section_id/url dicts
        url = self.kb_root + '/sections/{}/articles.json?include=users'.format(section_id)
        article_list = self.get_record_list(url)
        user_names = {}
        for user in article_list['users']:
            if user['id'] not in user_names:
                user_names[user['id']] = user['name']
        for article in article_list['articles']:
            if article['source_locale'] != src_locale:
                continue
            if article['draft']:
                continue
            dita_name = None
            for mapping in ditamap:
                if mapping['id'] == article['id']:
                    dita_name = mapping['dita']
                    break
            section_articles.append({'id': article['id'], 'title': article['title'], 'dita': dita_name,
                                     'author': user_names[article['author_id']],
                                     'section_id': section_id,
                                     'created_at': article['created_at'], 'url': article['html_url']})
        list_fname = 'section_{}_article_inventory.json'.format(section_id)
        write_to_json(section_articles, self.product_cache, list_fname)
        print('Inventory written')

    def take_localized_article_inventory(self, inventory=True):
        """
        Writes a list of localized articles to cache.
        Prerequisite: Run take_inventory() first to refresh the article data.
        :param inventory: Whether or not a current inventory exists.
        :return: None
        """
        if inventory is False:
            print('Taking inventory...')
            self.take_inventory()
        inventory = read_from_json(os.path.join(self.product_cache, self.product_inventory))
        # with open(os.path.join(self.product_cache, self.product_inventory), mode='r') as f:
        #     inventory = json.load(f)
        localized_articles = []
        for article in inventory:
            if article['source_locale'] != 'en-us':  # not one of ours
                continue
            url = self.kb_root + '/articles/{}/translations/missing.json'.format(article['id'])
            print('Checking translations for {}'.format(article['id']))
            missing = self.get_record(url)
            if not missing['locales']:
                localized_articles.append(article)
        write_to_json(localized_articles, self.product_cache, 'kb_localized_article_inventory.json')
        print('{} articles in loc inventory'.format(len(localized_articles)))

    def take_image_inventory(self, backup_folder):
        """
        Reads the files written to a backup folder and create a JSON inventory of all images in the files.
        Prerequisites:
        1. Take an inventory of articles for the HC or the category (e.g., agent or admin categories in Support).
        See take_inventory() method.
        2. Write the files in the article inventory to the backups folder. See backup_inventory() method.
        3. Pass the backup folder name to this method.
        :param backup_folder: Folder in backups containing the article files
        :return: None
        """
        image_list = []
        folder_path = os.path.join(os.sep, *self.settings['backups'].split('/'), backup_folder)
        files = glob.glob(os.path.join(folder_path, '*.html'))
        for file in files:
            tree = create_tree(file)
            img_links = tree('img')
            for image in img_links:
                base_name = os.path.basename(image['src'])
                image_list.append(base_name)
        image_list = list(set(image_list))      # a set is not JSON-serializable
        write_to_json(image_list, self.product_cache, f'kb_image_inventory_{backup_folder}.json')

    def backup_inventory(self, inventory, folder_name, locale='en-us'):
        folder_path = os.path.join(os.sep, *self.settings['backups'].split('/'), folder_name)
        print(folder_path)
        if os.path.exists(folder_path):
            print(f'A folder named {folder_name} already exists. Exiting.')
            exit()
        os.makedirs(folder_path)
        article_list = read_from_json(os.path.join(self.product_cache, inventory))
        for article in article_list:
            translation = self.get_translation(article['id'], locale)
            markup = get_page_markup(translation)
            if markup is None:
                continue
            filename = '{}.html'.format(translation['source_id'])
            with open(os.path.join(folder_path, filename), mode='w', encoding='utf-8') as f:
                f.write(markup)
            print(f'{filename} written')
        print(f'Package created at {folder_path}')

    def backup_raw_translation_inventory(self, folder_name):
        locales = 'de', 'es', 'fr', 'ja', 'pt-br'
        folder_path = os.path.join(os.sep, *self.settings['backups'].split('/'), folder_name, self.subdomain)
        print(folder_path)
        if os.path.exists(folder_path):
            print(f'A folder named {folder_name} already exists. Exiting.')
            exit()
        os.makedirs(folder_path)
        article_list = read_from_json(os.path.join(self.product_cache, 'kb_localized_article_inventory.json'))
        for locale in locales:
            for article in article_list:
                translation = self.get_translation(article['id'], locale)   # just get the raw translation (JSON?)
                if translation is None:
                    continue
                filename = '{}_{}.html'.format(locale, translation['source_id'])
                with open(os.path.join(folder_path, filename), mode='w', encoding='utf-8') as f:
                    f.write(translation['body'])
                print(f'{filename} written')
        print(f'Package created at {folder_path}')

    def get_articles_by_docs_team(self):
        cache_file = os.path.join(self.docs_team_cache, 'team_articles.json')
        backup(cache_file)
        team_articles = read_from_json(cache_file)
        date_times = []
        [date_times.append(article['created_at']) for article in team_articles]
        start_date = arrow.get(max(date_times))
        subdomains = 'support', 'chat', 'bime', 'help'
        docs_team = read_from_json(os.path.join(self.docs_team_cache, 'members.json'))
        for subdomain in subdomains:
            with open(os.path.join('cache', subdomain, self.product_inventory), mode='r') as f:
                inventory = json.load(f)
            for article in inventory:
                created_at = arrow.get(article['created_at'])
                if article['author'] in docs_team and created_at > start_date:
                    team_articles.append(article)
        write_to_json(team_articles, cache_file)
        write_to_excel(team_articles, self.docs_team_cache, 'team_articles.xlsx')
        print('Articles written to docs_team cache')

    def update_author(self, article_id, author_id):
        """
        Update the author assigned to an article
        :param article_id: HC article id
        :param author_id: Zendesk user id of the new author
        :return: nothing
        """
        url = self.kb_root + '/articles/{}.json'.format(article_id)
        payload = {'article': {'author_id': author_id}}
        response = self.put_record(url, payload=payload)
        if response:
            print('Successfully changed the author')
