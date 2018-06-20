import configparser
import os
import re
import glob
import shutil
import json
from zipfile import ZipFile
from ftplib import FTP

import arrow
from bs4 import Comment
from YamJam import yamjam
from zep.zendesk import KB
from zep.helpers import create_tree, get_page_markup, get_id_from_filename, rewrite_file, read_from_json, write_to_json


class Handoff:

    def __init__(self, name, product):
        config = configparser.ConfigParser()
        config.read('tools.ini')
        self.settings = config['HANDOFFS']
        self.name = name
        self.product = product
        self.base_path = os.path.join(os.sep, *self.settings['path'].split('/'))
        self.image_path = os.path.join(self.base_path, 'src')
        self.handoff_folder = os.path.join(self.base_path, self.name, self.product)
        self.localized_folder = os.path.join(self.handoff_folder, 'localized')
        self.article_registry = os.path.join('cache', self.product, 'localized_articles.json')
        self.image_registry = os.path.join('cache', self.product, 'localized_images.json')
        self.locales = self.settings['locales'].split(',')
        self.vendor_settings = config['VENDOR']
        if 'name' in self.vendor_settings:
            self.vendor_ftp = {'vendor': self.vendor_settings['name'],
                               'host': self.vendor_settings['ftp_host'],
                               'user': self.vendor_settings['ftp_user'],
                               'password': self.vendor_settings['ftp_password'],
                               'folder': self.vendor_settings['ftp_folder']}
        else:
            self.vendor_ftp = {'vendor': yamjam()['VENDOR_NAME'],
                               'host': yamjam()['VENDOR_FTP_HOST'],
                               'user': yamjam()['VENDOR_FTP_USER'],
                               'password': yamjam()['VENDOR_FTP_PASSWORD'],
                               'folder': yamjam()['VENDOR_FTP_FOLDER']}

    def verify_handoff_exists(self, localized=False):
        if localized:
            path = self.localized_folder
            msg = 'Can\'t find the localized files. No folder named \'localized\' or handoff doesn\'t exist.  Exiting.'
        else:
            path = self.handoff_folder
            msg = 'A handoff with that name doesn\'t exist. Exiting.'

        if os.path.exists(path):
            return True
        else:
            print(msg)
            exit()

    @staticmethod
    def read_registry(json_file):
        with open(json_file, mode='r') as f:
            data = json.load(f)
        return data

    @staticmethod
    def write_registry(json_file, registry):
        with open(json_file, mode='w') as f:
            json.dump(registry, f, sort_keys=True, indent=2)

    def get_localized_files(self, locale):
        file_path = os.path.join(self.localized_folder, locale.upper(), 'articles')
        return glob.glob(os.path.join(file_path, '*.html'))

    def write_files(self, loader='_loader.txt'):
        """
        Creates a handoff folder, gets specified en-us articles from HC, and writes them in the folder.

        :param loader: custom name of file with list of article ids to download
        :return: boolean
        """
        if os.path.exists(self.handoff_folder):
            print('A handoff with that name already exists. Exiting.')
            exit()
        article_list = []
        with open(os.path.join(self.base_path, loader), mode='r') as f:
            for line in f:
                article_list.append(int(line.strip()))            # [203660036, 203664356, 203663816]
        file_path = os.path.join(self.handoff_folder, 'articles')
        os.makedirs(file_path)
        handoff_list = '{} handoff files:\n\n'.format(self.name)
        kb = KB(self.product)
        for article in article_list:
            translation = kb.get_translation(article, 'en-us')
            if translation:
                if translation['source_id'] == 203661526:     # skip voice pricing article
                    continue
            else:
                print('{} in loader.txt does not exist on Help Center'.format(article))
                continue
            markup = get_page_markup(translation)
            if markup is None:
                continue
            filename = '{}.html'.format(translation['source_id'])
            with open(os.path.join(file_path, filename), mode='w', encoding='utf-8') as f:
                f.write(markup)
            print('{} written'.format(filename))
            handoff_list += '{} - "{}"\n'.format(filename, translation['title'])
        with open(os.path.join(file_path, 'handoff_list.txt'), mode='w', encoding='utf-8') as f:
            f.write(handoff_list)
        handoff_log = read_from_json(os.path.join(kb.shared_folder, 'handoff_log.json'))
        handoff_log[self.product].append({'date': self.name, 'files': article_list})
        write_to_json(handoff_log, kb.shared_folder, 'handoff_log.json')
        print('Package created at {}'.format(self.handoff_folder))

    def check_images(self, exclude=None):
        """
        Lists all the images not in https://zen-marketing-documentation.s3.amazonaws.com/docs/en.
        Ask writer to fix in source and html files.

        :param exclude: list of article ids that use English images in localized versions
        :return: boolean
        """
        self.verify_handoff_exists()

        file_path = os.path.join(self.handoff_folder, 'articles')
        files = glob.glob(os.path.join(file_path, '*.html'))
        missing_images = ''
        for file in files:
            if exclude and get_id_from_filename(file) in exclude:       # or?
                continue

            tree = create_tree(file)
            images = tree.find_all('img')
            for image in images:
                src = image['src']
                if 'zen-marketing-documentation' in src or 'embed-ssl.wistia.com' in src:
                    continue
                missing_images += '* in {} -> {}\n'.format(os.path.basename(file), src)

        if missing_images:
            print('The following images are not on S3:')
            print(missing_images)
        else:
            print('All image links point to S3!\n')

    def copy_images(self, months=4, exclude=None):
        """
        Parses articles in handoff package and copies recently updated en-us images from s3 folder
        to handoff folder.

        :param months: number of months when en-us images were last updated
        :param exclude: list of article ids that use English images in localized versions
        :return:
        """
        self.verify_handoff_exists()

        # Create images folder in handoff folder
        images_path = os.path.join(self.handoff_folder, 'images')
        images_path_fullsize = os.path.join(images_path, 'fullsize')
        images_path_resized = os.path.join(images_path, 'resized')
        if not os.path.exists(images_path):
            os.makedirs(images_path_fullsize)
            os.makedirs(images_path_resized)

        # Get fnames of images in s3 folder that were updated in the last x months
        src_images = []
        now = arrow.utcnow()
        files = glob.glob(os.path.join(self.image_path, '*.*'))
        for file in files:
            modified_at = arrow.get(os.path.getmtime(file))
            if modified_at > now.replace(months=-months):
                src_images.append(os.path.basename(file))

        # Parse each article in handoff_folder and move recently updated images to handoff package
        file_path = os.path.join(self.handoff_folder, 'articles')
        files = glob.glob(os.path.join(file_path, '*.html'))
        copied = []
        skipped = []
        for file in files:
            if exclude and get_id_from_filename(file) in exclude:       # or?
                continue

            tree = create_tree(file)
            images = tree.find_all('img')
            for image in images:
                image_name = os.path.basename(image['src'])
                if image_name in src_images:
                    if image_name not in copied:
                        src_image_path = os.path.join(self.image_path, image_name)
                        if 'width' in image.attrs:
                            shutil.copy(src_image_path, images_path_fullsize)
                        else:
                            shutil.copy(src_image_path, images_path_resized)
                        copied.append(image_name)
                else:
                    if image_name not in skipped:
                        skipped.append(image_name)

        print('\nImages copied (on s3 and updated in the last {} months): \n{}'.format(months, '\n'.join(copied)))
        print('\nImages not copied: \n{}'.format('\n'.join(skipped)))

    def strip_comments(self, write=True):
        self.verify_handoff_exists()

        print('\n')
        file_path = os.path.join(self.handoff_folder, 'articles')
        files = glob.glob(os.path.join(file_path, '*.html'))
        for file in files:
            if get_id_from_filename(file) == 203661526:        # voice pricing article - don't modify this file
                continue
            tree = create_tree(file)
            count = 0
            comments = tree.find_all(text=lambda text: isinstance(text, Comment))
            for comment in comments:
                comment.extract()
                count += 1
            if write and count > 0:
                rewrite_file(file, tree)

            print('Stripped {} comments in {}'.format(count, os.path.basename(file)))

    def zip_files(self):
        self.verify_handoff_exists()
        os.chdir(self.handoff_folder)
        archive_name = self.name + '_' + self.product + '.zip'
        folders = (os.path.join('articles'), os.path.join('images'))
        with ZipFile(archive_name, 'w') as myzip:
            for folder in folders:
                files = glob.glob(os.path.join(folder, '*.*'))
                for file in files:
                    myzip.write(file)
        print('{} created in the handoff folder'.format(archive_name))

    def upload_handoff(self):
        self.verify_handoff_exists()
        archive_name = self.name + '_' + self.product + '.zip'
        zip_file = os.path.join(self.handoff_folder, archive_name)
        if not os.path.exists(zip_file):
            print('No zip file exists for this handoff. Run the package command.')
            exit()
        with FTP(self.vendor_ftp['host']) as ftp:
            ftp.login(self.vendor_ftp['user'], self.vendor_ftp['password'])
            ftp.cwd(self.vendor_ftp['folder'])
            ftp_command = 'STOR {}'.format(archive_name)
            ftp.storbinary(ftp_command, open(zip_file, 'rb'))
            # ftp.dir()                                                              # for testing
        print('{} uploaded to the {} server'.format(archive_name, self.vendor_ftp['vendor']))

    def update_article_registry(self, locales, write):
        """
        Adds new localized articles in the handoff to the article registry for xrefs links.
        :param locales: tuple
        :param write: boolean
        :return: nothing
        """
        self.verify_handoff_exists(localized=True)
        if os.path.isfile(self.article_registry):
            registry = self.read_registry(self.article_registry)
        else:
            registry = {}                   # initialize a new registry dict {'en': ['one.jpg', ... ], ... }
            for locale in self.locales:
                registry[locale] = []

        if locales is None:                 # if locales not specified, use all locales
            locales = self.locales

        registry_updated = False

        for locale in locales:
            files = self.get_localized_files(locale)
            for file in files:
                article_id = get_id_from_filename(file)
                if article_id not in registry[locale]:         # new article! -> add to list of published
                    registry[locale].append(article_id)
                    print('Registering article: {}/{}'.format(locale, article_id))
                    if registry_updated is False:
                        registry_updated = True

        if registry_updated and write:
            self.write_registry(self.article_registry, registry)

        if registry_updated is False:
            print('Handoff contains no new articles to add to the registry.')

    def update_image_registry(self, locales, write):
        """
        Adds new localized images in the handoff to the image registry for src links.
        :param locales: tuple
        :param write: boolean
        :return: nothing
        """
        self.verify_handoff_exists(localized=True)
        if os.path.isfile(self.image_registry):
            registry = self.read_registry(self.image_registry)
        else:
            registry = {}                   # initialize a new registry dict {'en': ['one.jpg', ... ], ... }
            for locale in self.locales:
                registry[locale] = []

        if locales is None:                 # if locales not specified, use all locales
            locales = self.locales

        registry_updated = False

        for locale in locales:
            img_file_path = os.path.join(self.localized_folder, locale.upper(), 'images')
            image_files = glob.glob(os.path.join(img_file_path, '*.*'))
            for image_file in image_files:
                image = os.path.basename(image_file)
                if image not in registry[locale]:
                    print('Registering image: {}/{}'.format(locale, image))
                    registry[locale].append(image)
                    if registry_updated is False:
                        registry_updated = True

        if registry_updated and write:
            self.write_registry(self.image_registry, registry)

        if registry_updated is False:
            print('Handoff contains no new images to add to the registry.')

    def update_hrefs(self, locales=None, write=True):
        """
        Updates links to HC articles in the tree. Verifies that link is pointing to a localized HC article
        before updating it.
        :param locales: tuple
        :param write: boolean
        :return: nothing
        """
        self.verify_handoff_exists(localized=True)
        registry = self.read_registry(self.article_registry)

        if locales is None:                 # if locales not specified, use all locales
            locales = self.locales

        for locale in locales:
            files = self.get_localized_files(locale)
            for file in files:
                print('\nOpening {}{} for hrefs'.format(locale, file.split(locale.upper())[1]))
                tree = create_tree(file)
                links = tree.find_all('a', href=re.compile('/hc/en-us/'))
                for link in links:
                    if '/community/posts/' in link['href']:                # exclude links to community posts
                        continue
                    if '/article_attachments/' in link['href']:            # exclude in-text attachment links
                        continue
                    if '/#topic' in link['href']:
                        link['href'] = link['href'].split('/#topic')[0]    # /hc/fr/articles/206544348#topic_etm_2qc_5s

                    base_name = os.path.basename(link['href']).replace('#', '-').split('-')[0]
                    if '%' in base_name:
                        base_name = base_name.split('%')[0]
                    if '?' in base_name:
                        base_name = base_name.split('?')[0]

                    try:
                        int(base_name)
                    except ValueError:
                        print(' - Link is not an id number - {}'.format(base_name))
                        continue

                    if int(base_name) not in registry[locale]:            # does link have a known loc target?
                        print(' - Not localized in HC - {}'.format(link['href']))
                        continue

                    link['href'] = re.sub(r'hc/en-us', 'hc/{}'.format(locale), link['href'])
                    print(' - Updated xref - {}'.format(link['href']))

                if write:
                    rewrite_file(file, tree)

    def update_srcs(self, locales=None, write=True):
        """
        Updates links to S3 images in the tree. Verifies that link is pointing to a localized image on S3
        before updating it.
        :param locales:
        :param write:
        :return:
        """
        self.verify_handoff_exists(localized=True)
        registry = self.read_registry(self.image_registry)

        if locales is None:                 # if locales not specified, use all locales
            locales = self.locales

        for locale in locales:
            files = self.get_localized_files(locale)
            for file in files:
                #  /Users/cnadeau/production/handoffs/2016-11-18/chat/localized/
                print('\nOpening {}{} for srcs'.format(locale, file.split(locale.upper())[1]))
                tree = create_tree(file)
                img_links = tree.find_all('img', src=re.compile('/docs/en/'))
                for link in img_links:
                    base_name = os.path.basename(link['src'])
                    if base_name not in registry[locale]:
                        print(' - Not localized on S3 - {}'.format(link['src']))
                        continue
                    if locale == 'pt-br':
                        link['src'] = re.sub(r'docs/en', 'docs/{}'.format('pt'), link['src'])
                    else:
                        link['src'] = re.sub(r'docs/en', 'docs/{}'.format(locale), link['src'])
                    print(' - Updated src  - {}'.format(link['src']))

                if write:
                    rewrite_file(file, tree)

    def publish_handoff(self, locales=None, write=True):
        self.verify_handoff_exists(localized=True)
        kb = KB(self.product)

        if locales is None:                 # if locales not specified, use all locales
            locales = self.locales

        for locale in locales:
            print('\nPushing \'{}\' translations ...\n'.format(locale))
            files = self.get_localized_files(locale)
            for file in files:
                article_id = get_id_from_filename(file)
                print('Publishing {}...'.format(article_id))

                if article_id == 203661746:                            # if glossary, paste in HC by hand
                    print('Glossary, 203661746, skipped. Enter manually.')
                    continue

                # # if included in a later loc handoff that has since been delivered, skip
                # later_handoff = [115012184908, 115014797387, 203664326, 115012399428, 115014417408, 115012258168,
                #                  231747367, 115012794168, 115014810447]
                # if article_id in later_handoff:
                #     print(f'{article_id} skipped. Was delivered in a later handoff.')
                #     continue

                # #  id changes since handoff
                # changes = {235723507: 203664366, 235651328: 216207658, 235721887: 224858627}
                # if article_id in changes:
                #     article_id = changes[article_id]

                missing_translations = kb.get_missing_translations(article_id)
                if missing_translations is None:
                    print('Error getting missing translations for article {}. Exiting'.format(article_id))
                    exit()
                if locale in missing_translations:          # get http method to use for article
                    http_method = 'post'
                else:
                    http_method = 'put'

                tree = create_tree(file)
                title = ' '.join(tree.h1.stripped_strings)
                tree.h1.decompose()

                if http_method == 'post':
                    data = {'translation': {'locale': locale, 'title': title, 'body': str(tree), 'draft': False}}
                    if write:
                        print(f'- posting {article_id}')
                        kb.post_translation(article_id, payload=data)
                else:
                    data = {'translation': {'title': title, 'body': str(tree), 'draft': False}}
                    if write:
                        print(f'- putting {article_id}')
                        kb.put_translation(article_id, locale, payload=data)

# Testing
# if __name__ == '__main__':
#     ho = Handoff()
#     # ho.method()
