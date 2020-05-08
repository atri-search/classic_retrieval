.. MatchUp Information Retrieval Library documentation master file, created by
   sphinx-quickstart on Fri May  8 11:47:41 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MatchUp Information Retrieval Library
=================================================================

Match up is a PURE-Python library based on `Information Retrieval`_ (IR) concepts.
Here are implemented five IR models (`Boolean`_, `Vector Space`_, `Probabilistic`_, `Extended Boolean`_, `Generalized Vector`_
and `Belief Network`_) that can be tested and compared through a collection of documents and a query. The result will be
a query-based similarity rank that can be used to get insights about the collection.

.. _Information Retrieval: https://en.wikipedia.org/wiki/Information_retrieval
.. _Boolean: https://en.wikipedia.org/wiki/Boolean_model_of_information_retrieval
.. _Vector Space: https://en.wikipedia.org/wiki/Vector_space_model
.. _Probabilistic: https://en.wikipedia.org/wiki/Probabilistic_relevance_model
.. _Extended Boolean: https://en.wikipedia.org/wiki/Extended_Boolean_model
.. _Generalized Vector: https://en.wikipedia.org/wiki/Generalized_vector_space_model
.. _Belief Network: https://en.wikipedia.org/wiki/Bayesian_network

Simple Guide
------------

Vocabulary
^^^^^^^^^^

Let's start creating our collection. The first thing you should to do is import the Vocabulary object.::

    from matchup.structure.vocabulary import Vocabulary

The Vocabulary allows us to manage and process documents that will be part of our collection. Now we can build our
own vocabulary and import some files to it.::

    vocabulary = Vocabulary('path/to/save/collection')
    vocabulary.import_file('path/to/txt/file')
    vocabulary.import_folder('path/to/folder')

Well, we can see with this example that it is possible to import one single file, but you can also import all text files
in a directory. With that, the files are set, but not processed yet. Let's do this.::

    vocabulary.index_files()

We now have a data structure that allows us to query and extract insights from the collection that was built before.
If you want to persist it in memory, you can.::

    vocabulary.save()

And this method will persist the data structure on the path that had been set before, in Vocabulary constructor.
To retrieve this structure, it's simple.::

    vocabulary.import_collection()

Ok, that is all about the most important structure of this library. Now we'll learn how to make queries.

Query
^^^^^

Another pillar of this library is the query concept. Queries is responsible to extract insights about the collection.
The first to do working with queries, is to import the module.::

    from matchup.structure.query import Query

There are just one way to make queries: with plain text. If you want to do a query with a file, you need firstly process
this file in a string format, and then use it. Let's explore the Query structure with plain text approach.::

    query = Query(vocabulary=vocabulary)
    query.ask()  # here start an IO operation

You can also pass the answer with a param.::

    query.ask(answer="plain text")

After running this method, nothing happened !! This is because you haven't configured your search engine settings yet.
We can configure the search engine and execute the query at the same time.::

    # needs the import : from matchup.models.algorithms import Boolean
    response = query.search(model=Boolean())

That's it! Now we have a response for its query. The Boolean model it is the most simple IR model, it doesn't need any other param.
All the other models need weighting params, for example, that are configured by the named-params 'tf' and 'idf'. Learn more on Query
documentation.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   license
   help


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Status
------
Unstable. Building version 1.0
