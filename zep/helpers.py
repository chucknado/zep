import os
import json
import shutil

import yaml
import arrow
import pandas as pd
from bs4 import BeautifulSoup


# Data helpers

def write_to_cache(data, cache_path=None):
    """
    Writes a Python data structure to a .json file
    :param data: A Python data structure
    :param cache_path: Path and name of file to write
    :return: None
    """
    if cache_path is None:
        cache_path = os.path.join('cache', 'data.json')
    with open(cache_path, mode='w') as f:
        json.dump(data, f, sort_keys=True, indent=2)


def read_from_cache(cache_path=None):
    """
    Reads a .json file and converts it to a Python data structure
    :param cache_path: Path and name of file to read
    :return: Python data structure
    """
    if cache_path is None:
        cache_path = os.path.join('cache', 'data.json')
    with open(cache_path, mode='r') as f:
        data = json.load(f)
    return data


def read_from_json(path):
    """
    Converts a json file into a Python data structure
    :param path: Path and name of file to write
    :return: Python data structure
    """
    with open(path, 'r') as f:
        data = json.load(f)
    return data


def write_to_json(data, path, fname=None):
    """
    Writes a Python data structure to a .json file
    :param data: A Python data structure
    :param path: Path of file to write
    :param fname: Name of the json file to write
    :return: None
    """
    if fname is None:
        fname = 'data.json'
    file = os.path.join(path, fname)
    with open(file, mode='w') as f:
        json.dump(data, f, sort_keys=True, indent=2)


def read_from_yml(path):
    """
    Converts a yml file into a Python data structure
    :param path: Path and name of file to write
    :return: Python data structure
    """
    with open(path, 'r') as f:
        data = yaml.load(f)
    return data


def write_to_yml(data, path, fname=None):
    """
    Writes a Python data structure to a .yml file
    :param data: A Python data structure
    :param path: Path of file to write
    :param fname: Name of the yml file to write
    :return: None
    """
    if fname is None:
        fname = 'data.yml'
    file = os.path.join(path, fname)
    with open(file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)


def write_to_excel(data, path, fname=None):
    """
    Writes a list of dictionaries to a .xlsx file, where the worksheet's columns map to the dict keys
    :param data: A list of dictionaries
    :param path: Path to the Excel file
    :param fname: Name of the Excel file to write
    :return: None
    """
    if fname is None:
        fname = 'data.xlsx'
    df = pd.DataFrame(data)
    path = os.path.join(path, fname)  # save to public data folder
    df.to_excel(path, index=False)


def backup(src):
    utc = arrow.utcnow()
    dst = src.replace('.', '_{}.'.format(utc.timestamp))
    shutil.copy(src, dst)


# Parsing helpers

def get_page_markup(translation):
    body = '<html>' + translation['body'] + '</html>'   # to parse all the file (prevent `<p> </p>` None-type errors)
    tree = BeautifulSoup(body, 'lxml')
    if tree.html is None or tree.body is None:
        print('{}: tree.html or tree.body is None. Skipping'.format(translation['source_id']))
        return None
    head = tree.new_tag('head')
    meta = tree.new_tag('meta')
    meta['charset'] = 'utf-8'
    head.append(meta)
    tree.body.insert_before(head)
    h1 = tree.new_tag('h1')
    h1.string = translation['title']
    tree.body.insert_before(h1)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    markup = xml + str(tree)
    return markup


def create_tree(file, parser='lxml'):
    """
    Returns a BeautifulSoup tree object from the specified HTML file
    :param file: Full path to the HTML file to be read
    :param parser: 'lxml' for HTML files, or 'xml' for DITA files
    :return: A tree object
    """
    with open(file, mode='r', encoding='utf-8') as f:
        html_source = f.read()
    return BeautifulSoup(html_source, parser)


def rewrite_file(file, tree):
    """
    Writes a BeautifulSoup tree object to an HTML file
    :param file: Full path to the HTML file to be written
    :param tree: A BeautifulSoup tree object
    :return: None
    """
    contents = str(tree)
    if tree.find('html'):
        contents = contents.replace('<html>', '\n<html>', 1)
    with open(file, mode='w', encoding='utf-8') as f:
        f.write(contents)


def get_id_from_filename(file):
    """
    Gets Help Center article ID from HTML files written by zep methods
    :param file: Full path to the HTML file
    :return: Article ID (integer)
    """
    return int(os.path.basename(file)[:-5])


def get_dita_name_from_filename(file):
    """
    Gets DITA file name from HTML files transformed by Oxygen Author
    :param file: Full path to the transformed HTML file
    :return: Dita filename (string)
    """
    return os.path.basename(file)[:-5]
