import os
import unittest

from matchup.structure.Vocabulary import Vocabulary


class VocabularyTest(unittest.TestCase):
    def setUp(self):
        self._vocabulary = Vocabulary(os.path.abspath("tests/static/files"),
                                      stopwords=os.path.abspath("tests/static/pt-br.txt"),)

    def test_import_file(self):
        file = os.path.abspath("tests/static/files/d1.txt")
        self.assertTrue(self._vocabulary.import_file(file))
        self.assertTrue(file in self._vocabulary.file_names)

    def test_import_folder(self):
        folder = os.path.abspath("tests/static/files")
        self.assertTrue(self._vocabulary.import_folder(folder))

        self.assertTrue(len(self._vocabulary.file_names) == 20)

    def test_import_vocabulary(self):
        self.assertTrue(self._vocabulary.import_collection())
        self.assertTrue(self._vocabulary.keys is not None)
        self.assertTrue('brasil' in self._vocabulary.keys)

    def test_generate_vocabulary(self):
        self.assertTrue(not self._vocabulary.keys)

        folder = os.path.abspath("tests/static/files")
        self._vocabulary.import_folder(folder_path=folder)

        self._vocabulary.generate_collection()

        self.assertTrue('brasil' in self._vocabulary.keys)
