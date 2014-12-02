"""Python module for Yummly API: https://developer.yummly.com
"""

from functools import wraps
import json

import requests
from requests.exceptions import Timeout

import models


# NOTE: Have found that Yummly's API "hangs" so it might be a good idea to have
# some reasonable timeout and handle appropriately.
TIMEOUT = 5.0
RETRIES = 0


def handle_errors(func):
    """Decorator for handling Yummly errors"""
    @wraps(func)
    def decorated(self, *args, **kargs):
        # NOTE: `self` is the class this decorator wraps.

        # Attach a count attribute to the function so we have a hook to test
        # that retry works.
        self._handle_errors_count = 0

        # try to get response until retry limit reached
        for retry in xrange(0, self.retries + 1):
            try:
                response = func(self, *args, **kargs)
            except Timeout:
                # stop retrying after reaching max
                if retry == self.retries:
                    raise

                self._handle_errors_count += 1

        status = response.status_code

        if status != 200:
            if status == 409:
                raise YummlyError(
                    'API ID/key are invalid or API rate limit exceeded')
            else:
                # error ocurred which may not be documented
                response.raise_for_status()

        return response

    return decorated


class YummlyError(Exception):
    """Exception class for Yummly errors"""
    pass


class Client(object):
    """Client class to connect to Yummly API: https://developer.yummly.com

    :param api_id: Yummly API ID
    :param api_key: Yummly API Key
    :param timeout: API request timeout
    :param retries: Number of times to retry request if timeout received
    """

    # API URLs
    URL_BASE = 'http://api.yummly.com/v1/api'
    URL_GET = URL_BASE + '/recipe/'
    URL_SEARCH = URL_BASE + '/recipes'
    URL_META = URL_BASE + '/metadata'

    METADATA = {
        'ingredient': models.MetaIngredient,
        'holiday': models.MetaHoliday,
        'diet': models.MetaDiet,
        'allergy': models.MetaAllergy,
        'technique': models.MetaTechnique,
        'cuisine': models.MetaCuisine,
        'course': models.MetaCourse,
        'source': models.MetaSource,
        'brand': models.MetaBrand,
    }

    def __init__(self,
                 api_id=None,
                 api_key=None,
                 timeout=TIMEOUT,
                 retries=RETRIES):
        self.api_id = api_id
        self.api_key = api_key

        assert(timeout >= 0)
        self.timeout = timeout

        assert(isinstance(retries, int) and retries >= 0)
        self.retries = retries or 0

    def recipe(self, recipe_id):
        """Yummly get recipe API request

        :param recipe_id: recipe id
        """

        url = self.URL_GET + recipe_id
        response = self._request(url)
        result = self._extract_response(response)

        # NOTE: due to `yield` being a keyword, use `yields` instead
        result['yields'] = result.get('yield', '')

        recipe = models.Recipe(**result)

        return recipe

    def search(self, q, maxResult=40, start=0, **params):
        """Yummly search recipe API request

        :param q: search string
        :param maxResult: max results
        :param start: pagination offset in # of records (e.g. start=5 means
            skip first 5 results)
        :param **params: optional kargs corresponding to Yummly supported
            search parameters
        """

        url = self.URL_SEARCH

        # copy params to leave source unmodified
        params = params.copy()
        params.update({
            'q': q,
            'maxResult': maxResult,
            'start': start
        })

        response = self._request(url, params=params)
        result = self._extract_response(response)

        search_result = models.SearchResult(**result)

        return search_result

    def metadata(self, key):
        """Return metadata for given `key`."""
        MetaClass = self.METADATA.get(key)

        if not MetaClass:
            raise YummlyError(
                'Invalid metadata key. '
                'Valid keys are:' + ', '.join(self.METADATA.keys()))

        url = '{0}/{1}'.format(self.URL_META, key)
        response = self._request(url)

        try:
            data = [MetaClass(**md) for md in self._extract_metadata(response)]
        except Exception:
            raise YummlyError(
                'Could not extract metadata due to malformed data')

        return data

    @handle_errors
    def _request(self, url, params=None):
        """Generic yummly request which attaches meta info (e.g. auth)

        :param url: URL of endpoint
        :param params: GET params of request
        """

        # set auth headers
        headers = {
            'X-Yummly-App-ID':  self.api_id,
            'X-Yummly-App-Key': self.api_key,
        }

        response = requests.get(url,
                                params=params,
                                headers=headers,
                                timeout=self.timeout)

        return response

    def _extract_response(self, response):
        """Extract data from api resposne"""
        return response.json()

    def _extract_metadata(self, response):
        """Extract data from metadata response

        NOTE: metadata responses are jsonp strings of the form:
            set_metadata('meta name', [{...}, {...}, ...]);
        """

        text = response.text
        start = text.index('[')
        end = text.rfind(']') + 1
        parsed = text[start:end]

        return json.loads(parsed)

    def _filter_data(self, data, Model):
        """Filter data using fields supported by Model."""
        filtered = {}
        for f in Model._get_fields():
            if f in data:
                filtered[f] = data[f]

        return filtered
