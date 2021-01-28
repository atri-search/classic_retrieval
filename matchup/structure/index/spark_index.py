import os
import shutil

from collections import defaultdict
from typing import DefaultDict, List, Set

from pyspark.context import SparkContext
from pyspark.rdd import RDD

from matchup.structure.index.base_index import Index
from matchup.structure.occurrence import Occurrence
from matchup.presentation.sanitizer import Sanitizer
from matchup.presentation.formats import get_file
from matchup.presentation.text import Term


class SparkTextIndex(Index):

    def __init__(self, spark: SparkContext):
        self.spark = spark
        self.rdd = None
        self.sanitizer = Sanitizer()

    def process(self, files: Set[str], **kwargs) -> None:
        """
            This function try to process all content of files, generating
            the index data structure ready for use.
        :return: None
        """

        self.rdd = SparkTextIndex.__process(self.spark, files, self.sanitizer)

        invertedfile = self.rdd.collect()
        for term, occ in invertedfile:
            print(20*'-')
            print(f"{term}: {occ}")
            print(20*'-')

        file_path = kwargs.get("path")
        self.save(path=file_path)
    
    @staticmethod
    def __process(spark, files, sanitizer) -> RDD:
        collectionRDD: RDD = spark.wholeTextFiles(','.join(files)) # RDD de tuplas (nome_arquivo, conteudo)
        sanitizedRDD: RDD = collectionRDD.flatMapValues(lambda c: SparkTextIndex.__process_file(c, sanitizer))  # RDD de tuplas (nome_arquivo, tokens)
        dictionaryRDD: RDD = sanitizedRDD.flatMap(SparkTextIndex.__create_dict) # RDD de dicionarios (pares termo, [ocorrencias])
        invertedRDD: RDD = dictionaryRDD.reduceByKey(lambda x, y: x + y).mapValues(SparkTextIndex.__merge) # RDD com indice invertido
        sortedRDD: RDD = invertedRDD.mapValues(lambda  o:  sorted(o, key=Occurrence.doc))
        
        return sortedRDD

    @staticmethod
    def __process_file(content, sanitizer) -> list:
        number_line = 1
        new_content = []
        for line in content.split("\n"):
            new_content.append(sanitizer.sanitize_line(line, number_line))
            number_line += 1
        return new_content

    @staticmethod
    def __create_dict(args):
        """
            Function that push all file terms in index
        :param terms: list with all file terms
        :param file_name: path of file
        :return: None
        """
        file_name, terms = args
        return [(term.word, [Occurrence(file_name, term)]) for term in terms]
    
    @staticmethod
    def __merge(occ1: List[Occurrence]) -> List[Occurrence]:

        new_occurrences = []
        docs = []

        for o1 in occ1:
            if o1.doc() in docs:
                idx = docs.index(o1.doc())
                new_occurrences[idx].add(position=o1.positions[0])
            else:
                docs.append(o1.doc())
                new_occurrences.append(o1)

        return new_occurrences 


    def load(self, **kwargs) -> Set[str]:
        """
            This is a function that recover the index previously generated.
        :return: Set of files that generated its index.
        """
        self.rdd = self.spark.pickleFile(kwargs.get("path"))
        return set()


    def save(self, **kwargs) -> bool:
        """
            Persist data structure on disc.
        :return: boolean flag that indicates if the data structure can be persisted.
        """
        file_path = kwargs.get("path")

        if os.path.exists(file_path):
            shutil.rmtree(file_path)

        self.rdd.saveAsPickleFile(file_path)

        return True


    def __str__(self) -> str:
        """
            Simple index string representation
        :return:
        """
        return f"<SparkTextIndex {self.spark}>"

    
    def __contains__(self, item: str) -> bool:
        """
            This function enables the user to make the associative operation with 'in'
        :param item: One keyword
        :return:
        """
        return item in self.rdd.map(lambda x: x[0]).collect()


    def __getitem__(self, item: str) -> List[Occurrence]:
        """
            Get some occurrences by keyword, or init it on data structure
        :param item: keyword
        :return:
        """
        filteredRDD: RDD = self.rdd.filter(lambda x: x[0] == item)
        if filteredRDD.isEmpty():
            return []
        return filteredRDD.first()[1]

    @property
    def keys(self) -> List[str]:
        """
            Get all keywords presents in vocabulary
        :return: list of all keywords
        """
        return self.rdd.map(lambda x: x[0]).collect()

    def maximum_frequencies_per_document(self) -> DefaultDict[str, float]:
        """
            Return one dictionary with structure : Document -> Maximum frequency of one term in it document.
        :return:
        """
        docsRDD: RDD = self.rdd.flatMap(lambda x: [(oc.doc(), oc.frequency) for oc in x[1]] ) # rdd de pares (doc, freq)
        pairs = docsRDD.reduceByKey(lambda f1, f2: max([f1, f2])).collect()
        maxfreq = defaultdict(float)
        for key, freq in pairs:
            maxfreq[key] = freq
        return maxfreq


    def documents_with_keywords(self, kwds: Set[str]) -> Set[str]:
        """
            Return one set of documents that contains the set of keywords passed with param.
        :param kwds: set of keywords
        :return:
        """
        filteredRDD = self.rdd.filter(lambda x: x[0] in kwds)
        return set(filteredRDD.flatMap(lambda x: [oc.doc() for oc in x[1]]).collect()) # rdd de pares (doc, freq)
