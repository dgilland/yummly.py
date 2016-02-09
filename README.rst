yummly.py
*********

|version| |license|

Python library for `Yummly API <https://developer.yummly.com>`_

**NOTE:** This library and its author are not affliated with Yummly.


Installation
============


::

    pip install yummly


Dependencies
============

- requests >= 1.1.0


Usage
=====

Use ``yummly.Client`` to create a client object to interact with the Yummly API.

The client accepts ``api_id``, ``api_key``, and ``timeout`` as init parameters:


.. code-block:: python

    from yummly import Client

    # default option values
    TIMEOUT = 5.0
    RETRIES = 0

    client = Client(api_id=YOUR_API_ID, api_key=YOUR_API_KEY, timeout=TIMEOUT, retries=RETRIES)

    search = client.search('green eggs and ham')
    match = search.matches[0]

    recipe = client.recipe(match.id)


Search Recipes
--------------

API endpoint: ``api.yummly.com/v1/api/recipes?<params>``

Search for recipes meeting certain criteria:


.. code-block:: python

    results = yummly.search('bacon')

    print('Total Matches:', results.totalMatchCount)
    for match in results.matches:
        print('Recipe ID:', match.id)
        print('Recipe:', match.recipeName)
        print('Rating:', match.rating)
        print('Total Time (mins):', match.totalTimeInSeconds / 60.0)
        print('----------------------------------------------------')


Limit your results to a maximum:


.. code-block:: python

    # return the first 10 results
    results = yummly.search('chicken marsala', maxResults=10)


Offset the results for pagination:


.. code-block:: python

    # return 2nd page of results
    results = yummly.search('pulled pork', maxResults=10, start=10)


Provide search parameters:


.. code-block:: python

    params = {
        'q': 'pork chops',
        'start': 0,
        'maxResult': 40,
        'requirePicutres': True,
        'allowedIngredient[]': ['salt', 'pepper'],
        'excludedIngredient[]': ['cumin', 'paprika'],
        'maxTotalTimeInSeconds': 3600,
        'facetField[]': ['ingredient', 'diet'],
        'flavor.meaty.min': 0.5,
        'flavor.meaty.max': 1,
        'flavor.sweet.min': 0,
        'flavor.sweet.max': 0.5,
        'nutrition.FAT.min': 0,
        'nutrition.FAT.max': 15
    }

    results = yummly.search(**params)


For a full list of supported search parameters, see section *The Search Recipes Call* located at: https://developer.yummly.com/intro

Example search response: https://developer.yummly.com/wiki/search-recipes-response-sample


Get Recipe
----------

API endpoint: ``api.yummly.com/v1/api/recipe/<recipe_id>``

Fetch a recipe by its recipe ID:


.. code-block:: python

    recipe = yummly.recipe(recipe_id)

    print('Recipe ID:', recipe.id)
    print('Recipe:', recipe.name)
    print('Rating:', recipe.rating)
    print('Total Time:', recipe.totalTime)
    print('Yields:', recipe.yields)
    print('Ingredients:')
    for ingred in recipe.ingredientLines:
        print(ingred)


Example recipe response: https://developer.yummly.com/wiki/get-recipe-response-sample

**NOTE:** Yummly's Get-Recipe response includes ``yield`` as a field name. However, ``yield`` is a keyword in Python so this has been renamed to ``yields``.


Search metadata
---------------

API endpoint: ``api.yummly.com/v1/api/metadata/<metadata_key>``

Yummly provides a metadata endpoint that returns the possible values for allowed/excluded ingredient, diet, allergy, and other search parameters:


.. code-block:: python

    METADATA_KEYS = [
        'ingredient',
        'holiday',
        'diet',
        'allergy',
        'technique',
        'cuisine',
        'course',
        'source',
        'brand',
        'restriction'
    ]

    ingredients = client.metadata('ingredient')
    diets = client.metadata('diet')
    sources = client.metadata('source')


**NOTE:** Yummly's raw API returns this data as a JSONP response which ``yummly.py`` parses off and then converts to a ``list`` containing instances of the corresponding metadata class.


API Model Classes
=================

All underlying API model classes are in ``yummly/models.py``. The base class used for all models is a modified ``dict`` class with attribute-style access (i.e. both ``obj.foo`` and ``obj['foo']`` are valid accessor methods).

A derived ``dict`` class was chosen to accommodate painless conversion to JSON which is a fairly common requirement when using ``yummly.py`` as an API proxy to feed your applications (e.g. a web app with ``yummly.py`` running on your server instead of directly using the Yummly API on the frontend).


Testing
=======

Tests are located in ``tests/``. They can be executed using ``pytest`` from the root directory using ``makefile`` or ``pytest``.


::

    # using makefile
    make test

    # using pytest directly
    py.test yummly


**NOTE:** Running the test suite will use real API calls which will count against your call limit. Currently, 22 API calls are made when running the tests.


Test Config File
----------------

A test config file is required to run the tests. Create ``tests/config.json`` with the following properties:

.. code-block:: javascript

    {
        "api_id": "YOUR_API_ID",
        "api_key": "YOUR_API_KEY"
    }


This file will be loaded automatically when the tests are run.


License
=======

This software is licensed under the MIT License.


TODO
====

- Provide helpers for complex search parameters like nutrition, flavors, and metadata


.. |version| image:: http://img.shields.io/pypi/v/yummly.svg?style=flat
    :target: https://pypi.python.org/pypi/yummly/

.. |license| image:: http://img.shields.io/pypi/l/yummly.svg?style=flat
    :target: https://pypi.python.org/pypi/yummly/
