"""
    The query module is responsible for encapsulating everything related to the process of creating a user query.
"""
from typing import List

from matchup.presentation.sanitizer import Sanitizer
from matchup.models.orchestrator import Orchestrator, ModelType
from matchup.structure.solution import Solution
from matchup.presentation.text import Term


class NoSuchAnswerException(RuntimeError):
    """
        Exception when no such answer (input) are given by user during a search method.
    """
    pass


class Query:
    """
        Represents the Query of the IR service.
        The query is responsible for processing and generating user input to search a previously built collection
    """
    def __init__(self, *, vocabulary):
        self._sanitizer = Sanitizer(stopwords_path=vocabulary.stopwords_path) if vocabulary.stopwords_path else \
            Sanitizer()
        self._orq = Orchestrator(vocabulary)
        self._answer = list()

    def ask(self, answer: str = None) -> None:
        """
            Make query since a command line prompt.
        :return: None
        """
        if not answer:
            message = "{0}\n{1: >18}".format(25*"= ", "Consulta: ")
            answer = input(message)
            self._answer = self._sanitizer.sanitize_line(answer, 1)
        else:
            number_line = 1
            text = answer.split("\n")
            terms = []
            for line in text:
                terms += self._sanitizer.sanitize_line(line, number_line)
                number_line += 1
            self._answer = terms

        self._orq.entry = self._answer

    @property
    def search_input(self) -> List[Term]:
        """
            Input property getter.
        :return:
        """
        return self._answer

    def search(self, *, model: ModelType = None, idf=None, tf=None, **kwargs) -> Solution:
        """
            Receive an IR model and execute the query based in user answer and the vocabulary.
        :param model: ModelType that represents the IR model
        :param idf: Describe the class  of IDF
        :param tf: Describe the class of TF
        :return: list of solution -> (document, score)
        """
        results = self._orq.search(model, idf, tf, **kwargs)
        return Solution(results)
