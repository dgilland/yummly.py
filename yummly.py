'''
Python module for Yummly API: https://developer.yummly.com
'''

import requests

# Yummly API: https://developer.yummly.com

# API URLs
URL_BASE    = 'http://api.yummly.com/v1'
URL_GET     = URL_BASE + '/api/recipe/'
URL_SEARCH  = URL_BASE + '/api/recipes'

# API auth properties which should be set externally
api_id  = None
api_key = None

# basic request config options
# @note: have found that Yummly's API "hangs" so it might be a good idea to have some reasonable timeout and handle appropriately
timeout = 5.0

class YummlyError( Exception ):
    '''Exception class for Yummly errors'''
    pass

### Methods for API get recipe and search recipes

def recipe( recipe_id ):
    url = URL_GET + recipe_id
    response    = _request( url )
    result      = _extract_response( response )
    return result

def search( q, limit=40, offset=0 ):
    '''
    Prepares yummly search API request

    :param q: search string
    :param limit: max results
    :param offset: pagination offset in # of records (e.g. offset=5 means skip first 5 results)

    '''

    url     = URL_SEARCH
    params  = {
        'q':            q,
        'maxResult':    limit,
        'start':        offset
    }

    response    = _request( url, params=params )
    results     = _extract_response( response )
    return results


### Helper functions

def handle_errors( fn ):
    '''Decorator for handling Yummly errors'''
    def handle( *args, **kargs ):
        response = fn( *args, **kargs )

        status = response.status_code

        if status != 200:
            if status == 409:
                raise YummlyError( 'API id and/or key are invalid or API rate limit exceeded' )
            else:
                # error ocurred which may not be documented
                response.raise_for_status()

        return response

    return handle

@handle_errors
def _request( url, params=None ):
    '''
    Generic yummly request which attaches meta info (e.g. auth)

    :param url: URL of endpoint
    :param params: GET params of request

    '''

    # auth headers
    headers = {
        'X-Yummly-App-ID':  api_id,
        'X-Yummly-App-Key': api_key,
    }

    response = requests.get( url, params=params, headers=headers, timeout=timeout )

    return response

def _extract_response( response ):
    '''Extract data from api resposne'''
    return response.json()

