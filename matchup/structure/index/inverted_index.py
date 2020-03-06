import pickle
from os import path
from collections import defaultdict
from typing import List, Set, DefaultDict

from matchup.structure.occurrence import Occurrence

from matchup.presentation.sanitizer import Sanitizer
from matchup.presentation.text import Term
from matchup.presentation.formats import ExtensionNotSupported, get_file


class InvertedIndex:
    def __init__(self):
        self._inverted_file = defaultdict(list)

    def __str__(self) -> str:
        """
            Transform an Vocabulary object in an String
        :return: String that represents the structure of vocabulary
        """
        vocabulary = ""
        for key in self._inverted_file.keys():
            vocabulary += str(key + ":" + str(self._inverted_file[key]) + "\n")
        return vocabulary

    def __contains__(self, item: str) -> bool:
        """
            This function enables the user to make the associative operation with 'in'
        :param item: keyword
        :return: boolean flag that return true if the keyword are in vocabulary
        """
        return item in self._inverted_file

    def __getitem__(self, item: str) -> List[Occurrence]:
        """
            Get some vocabulary occurrences by item, or init it on data structure
        :param item: keyword
        :return: Occurrences of keyword
        """
        return self._inverted_file[item]

    def load(self, file_path) -> Set[str]:
        """
            This is a function that recover the vocabulary previously generated.
        :return: set of files retrieved
        """
        self._inverted_file.clear()
        if path.exists(file_path):
            with open(file_path, mode='rb') as file:
                self._inverted_file = pickle.load(file)
                return self.__retrieve_file_names()
        raise FileNotFoundError

    def save(self, file_path) -> bool:
        """
            Persist data structure on disc.
        :return: boolean flag that indicates if the data structure can be persisted.
        """
        self.__sort()
        if self._inverted_file:
            with open(file_path, mode='wb') as file:
                pickle.dump(self._inverted_file, file)
            return True
        raise ReferenceError("You should to process some create_collection files")

    @property
    def keys(self) -> list:
        """
            Get all keywords presents in vocabulary
        :return: list of all keywords
        """
        return list(self._inverted_file.keys())

    def map_docs(self) -> DefaultDict[str, float]:
        map_docs = defaultdict(float)
        for key in self._inverted_file:
            for occurrence in self._inverted_file[key]:
                if map_docs[occurrence.doc()] < occurrence.frequency:
                    map_docs[occurrence.doc()] = occurrence.frequency
        return map_docs

    def process(self, files: Set[str], sanitizer: "Sanitizer" = None) -> None:
        """
            This function try to process all content of files that have been inserted before, generating
            the vocabulary data structure ready for use.
        :return: None
        """
        sanitizer = sanitizer if sanitizer else Sanitizer()

        for file_name in files:
            try:
                file = get_file(file_name)
            except ExtensionNotSupported:
                continue
            try:
                text_io = file.open()
                self.__process_file(file_name, text_io, sanitizer)
            except ExtensionNotSupported:
                continue
            finally:
                file.close()

    def __process_file(self, filename, content_file, sanitizer) -> None:
        number_line = 1
        for content_line in content_file:
            terms = sanitizer.sanitize_line(content_line, number_line)
            self.__push(terms, filename)
            number_line += 1

    def __push(self, terms: List[Term], file_name: str) -> None:
        """
            Function that push all file terms in vocabulary
        :param terms: list with all file terms
        :param file_name: path of file
        :return: None
        """
        for term in terms:
            try:
                idx = self._inverted_file[term.word].index(file_name)
                occurrence = self._inverted_file[term.word][idx]
                occurrence.add(position=term.position)

            except ValueError:
                occurrence = Occurrence(file_name, term)
                self._inverted_file[term.word].append(occurrence)

    def __retrieve_file_names(self) -> Set[str]:
        """
            Iterate the data structure retrieving the file names that generated it vocabulary
        :return: set of files retrieved
        """
        files = set()
        for keyword in self._inverted_file:
            for occurrence in self._inverted_file[keyword]:
                files.add(occurrence.doc())
        return files

    def __sort(self) -> None:
        """
            Order the documents in vocabulary structure.
        :return: None
        """
        for key in self._inverted_file:
            self._inverted_file[key] = sorted(self._inverted_file[key], key=Occurrence.doc)