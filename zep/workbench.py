import configparser
import os
import glob
import re
import shutil

from bs4 import BeautifulSoup
# from lxml import etree
from zep.zendesk import KB
from zep.helpers import write_to_json, read_from_json, create_tree, rewrite_file


class Workbench:
    def __init__(self, subdomain):
        self.config = configparser.ConfigParser()
        self.config.read('tools.ini')
        self.settings = self.config['KB']
        self.source_file_path = os.path.join(self.settings['workbench'], subdomain)
        self.product_cache = os.path.join('cache', subdomain)
        # self.source_docs_path = os.path.join(os.sep, 'Users', 'cnadeau', 'Google Drive, 'Zendesk User Guides')
        self.subdomain = subdomain

    def move_unused_images(self, live_images):
        images_in_use = read_from_json(os.path.join(self.product_cache, live_images))
        src_path = os.path.join(self.source_file_path, '_graphics')
        dst_path = os.path.join(self.source_file_path, '_graphics_unused')
        source_images = glob.glob(os.path.join(src_path, '*.*'))
        for file in source_images:
            file_name = os.path.basename(file)
            if file_name not in images_in_use:
                print(f'Moving {file_name}')
                src = file
                dst = os.path.join(dst_path, file_name)
                shutil.move(src, dst)

    def get_used_source_images(self, live_images):
        used_source_images = []
        images_in_use = read_from_json(os.path.join(self.product_cache, live_images))
        image_source_path = os.path.join(self.source_file_path, '_graphics')
        source_images = glob.glob(os.path.join(image_source_path, '*.*'))
        for image in source_images:
            image_name = os.path.basename(image)
            if image_name in images_in_use:
                used_source_images.append(image_name)
                print(f'Move {image_name}')
        write_to_json(used_source_images, self.product_cache, 'talk_used_source_images.json')

    # copy_used_images('talk_used_source_images.json')
    def copy_used_images(self, move_list):
        image_list = read_from_json(os.path.join(self.product_cache, move_list))
        src_path = os.path.join(self.source_file_path, '_graphics')
        dst_path = os.path.join(self.source_file_path, '_graphics_talk')
        for image in image_list:
            src = os.path.join(src_path, image)
            dst = os.path.join(dst_path, image)
            shutil.copy(src, dst)

    def check_plan_banners(self):
        plan_alt_text = {'plan_available_all.png': 'all plans',
                         'plan_available_all_orig.png': 'all original plans',
                         'plan_available_rpe.png': 'team professional and enterprise plans',
                         'plan_available_pe.png': 'professional and enterprise plans',
                         'plan_available_e.png': 'enterprise plan',
                         'plan_available_add_p_add_e.png': 'professional and enterprise add-ons',
                         'plan_available_add_p_e.png': 'professional add-on and enterprise plan',
                         'plan_available_add_e.png': 'enterprise add-on'}
        no_banner = []
        files = glob.glob(os.path.join(self.source_file_path, '*.dita'))
        for file in files:
            write = True
            tree = create_tree(file, 'xml')
            plan_image = tree.find(href=re.compile('plan_available_'))

            if plan_image is None:
                no_banner.append(os.path.basename(file))
                write = False

            elif plan_image.alt:
                # has alt tag, which replaced the deprecated alt attribute
                write = False

            elif 'alt' in plan_image.attrs:
                # has alt attribute; create alt tag based on attribute and delete attribute
                alt_tag = tree.new_tag('alt')
                plan_image.append(alt_tag)
                alt_tag.string = plan_image['alt']
                del plan_image['alt']  # not deleting

            else:
                # has no alt attribute; created alt tag based on image file name
                image_file = os.path.basename(plan_image['href'])
                if image_file in plan_alt_text:
                    alt_tag = tree.new_tag('alt')
                    plan_image.append(alt_tag)
                    alt_tag.string = plan_alt_text[image_file]
                else:
                    print(f'{os.path.basename(file)} - "plan_available" image not in dict')
                    write = False

            if write:
                rewrite_file(file, tree)
                print(f'{os.path.basename(file)} updated')

        print('\nThe following articles have no plan banners:\n')
        for article in no_banner:
            print(article)

    # --- Add alt text to plan banners -- #

    # def get_no_banner_alt_text(self):
    #     """
    #     Take article inventory (include Tips)
    #     """
    #     plan_alt_text = {'plan_available_all.png': 'all plans',
    #                      'plan_available_all_orig.png': 'all original plans',
    #                      'plan_available_rpe.png': 'team professional enterprise plans',
    #                      'plan_available_pe.png': 'professional enterprise plans',
    #                      'plan_available_e.png': 'enterprise plan',
    #                      'plan_available_add_p_add_e.png': 'professional and enterprise add-ons',
    #                      'plan_available_add_p_e.png': 'professional add-on and enterprise plan',
    #                      'plan_available_add_e.png': 'enterprise add-on'}
    #     no_banner = []
    #     updated_articles = []
    #     kb = KB(self.subdomain)
    #     article_list = read_from_json(os.path.join(kb.product_cache, 'kb_article_inventory.json'))
    #     for article in article_list:
    #         translation = kb.get_translation(article['id'])
    #         tree = BeautifulSoup(translation['body'], 'lxml')
    #         plan_image = tree.find(src=re.compile('plan_available_'))
    #         if plan_image is None:
    #             no_banner.append(article['url'])
    #         elif 'alt' not in plan_image.attrs:
    #             print(f'No alt attribute: {article["url"]}')
    #             image_file = os.path.basename(plan_image['src'])
    #             if image_file in plan_alt_text:
    #                 print(f'Adding alt attribute: {plan_image}')
    #                 plan_image['alt'] = plan_alt_text[image_file]
    #                 print(f'Updating: {article["url"]}')
    #                 data = {'translation': {'body': str(tree)}}
    #                 kb.put_translation(article['id'], 'en-us', payload=data)
    #                 updated_articles.append(article['url'])
    #             else:
    #                 print(f'{os.path.basename(file)} - "plan_available" image not in dict')
    #
    #     print('\nThe following articles have no plan banners:\n')
    #     for article in no_banner:
    #         print(article)
    #
    #     print('\nThe following articles with no alt text were updated:\n')
    #     for article in updated_articles:
    #         print(article)

    # def replace_href_in_source(self, new_href, old_href):
    #     parser = etree.XMLParser(recover=True)
    #     # new_href = 'http://zen-marketing-documentation.s3.amazonaws.com/docs/en/'
    #     # old_href = 'https://zen-marketing-documentation.s3.amazonaws.com/docs/en/'
    #
    #     files = glob.glob(os.path.join(self.source_docs_path, '*.dita'))
    #
    #     print(f'\nFOLDER: {self.source_file_path}\n')
    #     path_len = 16 + len(self.source_file_path) + 1
    #     for file in files:
    #         modified = False
    #         if file[path_len:] == 'voice_pricing.dita':         # don't check this file
    #             continue
    #         with open(file, mode='rb') as f:
    #             tree = etree.parse(f, parser)                   # returns an ElementTree
    #         for image in tree.iter('image'):
    #             href = image.attrib['href']
    #             if old_href in href:
    #                 image.attrib['href'] = re.sub(old_href, new_href, image.attrib['href'])
    #                 modified = True
    #                 print('  Updated image - {}'.format(image.attrib['href']))
    #
    #         # print(etree.tostring(tree))
    #         if modified:
    #             print('Modified: {}'.format(file[path_len:]))
    #             tree.write(file, encoding='utf-8', xml_declaration=True)
    #             print('\n-----\n')
