import os
import json
import yaml
import shutil

import arrow


class Ditamap:

    def __init__(self):
        self.shared_production_folder = os.path.join(os.sep, 'Volumes', 'GoogleDrive', 'Team Drives',
                                                     'Documentation', 'All products', 'production')
        self.ditamap_file = os.path.join(self.shared_production_folder, 'ditamap.yml')

    def open(self, hc=None):
        """
        Reads the ditamap.yml file in the shared production folder and returns a list of dicts. Can be filtered
        by Help Center. Returns all mappings by default.
        :param hc: (Optional) A Help Center subdomain ('support', 'chat', 'bime', etc) to filter the _ditamap
        :return: List of article mappings
        """
        with open(self.ditamap_file, 'r') as f:
            ditamap = yaml.load(f)
        if hc:
            hc_map = []
            for article in ditamap:
                if article['hc'] == hc:
                    hc_map.append(article)
            ditamap = hc_map
        return ditamap

    def save(self, ditamap):
        """
        Writes a ditamap list to the ditamap.yml file in the shared production folder.
        :param ditamap: A list of {id, hc, dita} dicts.
        :return: None
        """
        self.backup()
        with open(self.ditamap_file, 'w') as f:
            yaml.dump(ditamap, f, default_flow_style=False)

    def backup(self):
        """
        Creates a timestamped backup of the ditamap file in the production folder.
        :return: None
        """
        utc = arrow.utcnow()
        backup_file = 'ditamap_{}.yml'.format(utc.timestamp)
        dst = os.path.join(self.shared_production_folder, backup_file)
        src = self.ditamap_file
        shutil.copy(src, dst)

    def show(self, hc=None):
        """
        Pretty-print the _ditamap in the console.
        :param hc: A Help Center subdomain ('support', 'chat', 'bime', etc) to filter the _ditamap
        :return: None
        """
        ditamap = self.open(hc)
        print(json.dumps(ditamap, sort_keys=True, indent=2))
        print('\n{} articles in the _ditamap'.format(len(ditamap)))
