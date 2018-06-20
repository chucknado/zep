import os
import shutil
import unittest
import glob

from zep.zendesk import KB
from zep.handoff import Handoff


class HandoffExistsTestCase(unittest.TestCase):

    def setUp(self):
        self.name = '2112_12_12'
        self.test_dir = os.path.join('../', 'handoffs', self.name)
        os.makedirs(self.test_dir)

    def test_handoff_exists(self):
        ho = Handoff(self.name)
        self.assertTrue(ho.verify_handoff_exists(),
                        msg='verify_handoff_exists() does not detect an existing package')

    def test_handoff_does_not_exist(self):
        ho = Handoff('rainbows_and_unicorns')
        with self.assertRaises(SystemExit):
            ho.verify_handoff_exists()

    def tearDown(self):
        shutil.rmtree(self.test_dir)


class CreateHandoffTestCase(unittest.TestCase):

    def setUp(self):
        self.loader = os.path.join('..', 'handoffs', '_test_loader.txt')
        with open(self.loader, mode='w', encoding='utf-8') as f:
            f.write('203661596\n203690856')

    def test_download_files_to_handoff_folder(self):
        name = '2112-12-13'
        self.handoff_dir = os.path.join('..', 'handoffs', name)
        ho = Handoff(name)
        ho.write_files(loader=os.path.basename(self.loader))
        results = glob.glob(os.path.join(self.handoff_dir, 'articles', '*.html'))
        files = [os.path.basename(file_path) for file_path in results]
        self.assertEqual(files, ['203661596.html', '203690856.html'])

    def tearDown(self):
        os.remove(self.loader)
        shutil.rmtree(self.handoff_dir)


class PackageTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dirs = []
        packages = ['package1', 'package2']
        for package in packages:
            folder_path = os.path.join('../', 'packages', package)
            os.mkdir(folder_path)
            cls.test_dirs.append(folder_path)       # for teardown
        files = ['fname1.html', 'fname2.html']
        for file in files:
            file_path = os.path.join(cls.test_dirs[0], file)
            with open(file_path, mode='w', encoding='utf-8') as f:
                f.write('html here')

    def test_package_obj_created(self):
        package = Package('package1')
        self.assertIsInstance(package, Package)

    def test_package_exists(self):
        package = Package('package1')
        self.assertTrue(package.verify_package_exists(),
                        msg='verify_package_exists() does not detect an existing package')

    def test_package_does_not_exist(self):
        package = Package('rainbows_and_unicorns')
        with self.assertRaises(SystemExit):
            package.verify_package_exists()

    def test_get_package_files(self):
        package = Package('package1')
        self.assertEqual(len(package.get_files()), 2,
                         msg='get_files() method does not return all the HTML files in the list')

    def test_get_package_files_from_empty_directory(self):
        package = Package('package2')
        self.assertEqual(len(package.get_files()), 0,
                         msg='get_files() does not return an empty list when folder is empty')

    @classmethod
    def tearDownClass(cls):
        for test_dir in cls.test_dirs:
            shutil.rmtree(test_dir)


class HelpCenterTestCase(unittest.TestCase):

    def test_get_categories(self):
        hc = KB()
        self.assertIsInstance(hc, KB)


if __name__ == '__main__':
    unittest.main()



# def test_get_localized_files(self):
#     ho = Handoff('ho1')
#     self.assertEqual(len(ho.get_localized_files()), 2,
#                      msg='get_localized_files() method does not return all the HTML files in the list')
#
# def test_get_localized_files_from_empty_directory(self):
#     ho = Handoff('ho2')
#     self.assertEqual(len(ho.get_localized_files()), 0,
#                      msg='get_localized_files() does not return an empty list when folder is empty')



# class HelpCenterTestCase(unittest.TestCase):
#
#     def test_helpcenter_obj_created(self):
#         hc = HelpCenter()
#         self.assertIsInstance(hc, HelpCenter)

