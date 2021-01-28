# testando a lib com o spark
from matchup.structure.vocabulary import Vocabulary
from matchup.structure.query import Query
from matchup.models.algorithms import Boolean
from matchup.structure.index.spark_index import SparkTextIndex

# configure spark context
from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("MatchUpSpark").setMaster("local[8]") 
sc = SparkContext(conf=conf)

vocabulary = Vocabulary("./samples/output", indexer=SparkTextIndex(sc))
vocabulary.import_folder("./samples/dataset")
vocabulary.index_files()

# query = Query(vocabulary=vocabulary)
# query.ask(answer="romario")  # here start an IO operation

# response = query.search(model=Boolean())
# print(response.results)

while True:
    pass