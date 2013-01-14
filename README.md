# yummly.py

Python library for Yummly API: https://developer.yummly.com

Version: 0.1.0

## Installation

### Using setup.py

```bash
$ python setup.py install
```

### Current Dependencies

- requests==1.1.0
- nose==1.2.1 (for testing)

## Usage

```python
import yummly
```

### Configuration

The Yummly API requires an ID and Key. This can be set by doing:

```python
yummly.api_id = YOUR_API_ID
yummly.api_key = YOUR_API_KEY
```

### Search Recipes

Search for recipes meeting certain criteria:

```python
results = yummly.search('bacon')
```

**NOTE:** Currently, only search by phrase, `q`, is supported. Future versions will add support for additional criteria.

Limit your results to a maximum:

```python
# return the first 10 results
results = yummly.search('chicken marsala', limit=10)
```

Offset the results for pagination:

```python
# return 2nd page of results
results = yummly.search('pulled pork', limit=10, offset=10)
```

Example search response: https://developer.yummly.com/wiki/search-recipes-response-sample

### Get Recipe

Fetch a recipe by its recipe ID:

```python
recipe = yummly.recipe(recipe_id)
```

Example recipe response: https://developer.yummly.com/wiki/get-recipe-response-sample

## Testing

Tests are located in `tests/`. They can be executed with `nose` by running `run_tests.py` from the root directory.

```bash
$ python run_tests.py
```

### Test Config File

A test config file is required to run the tests. Create `tests/config.json` with the following properties:

```json
{
    "api_id": "your api id",
    "api_key": "your api key"
}
```

This file will be loaded automatically when the tests are run.

## TODO

- Support all search criteria
- Options for sorting search results
