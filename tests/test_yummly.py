
import os
import unittest
import json
from time import sleep

import yummly

HERE = os.path.dirname(__file__)

class TestYummly( unittest.TestCase ):

    @classmethod
    def setUpClass( cls ):
        config_file = os.path.join( HERE, 'config.json' )

        with open( config_file ) as f:
            config = json.load(f)

        cls.yummly = yummly
        cls.yummly.api_id  = config.get('api_id')
        cls.yummly.api_key = config.get('api_key')

        cls.sample_recipe_id = 'Hot-Turkey-Salad-Sandwiches-Allrecipes'
        # cache recipe results to decrease API hits
        cls.sample_recipe = None

    def setUp( self ):
        # wait some time inbetween tests for throttling self
        TestYummly.wait()

    @staticmethod
    def wait():
        sleep(0.5)

    @staticmethod
    def verify_fields( expected, actual ):
        for field in expected:
            try:
                assert( field in actual )
            except AssertionError:
                raise AssertionError('Missing field:' + field)

        return True

    def test_search( self ):
        '''Test basic search functionality'''

        q = 'chicken casserole'
        maxResult = 5

        results = self.yummly.search( q, maxResult=maxResult )

        # verify fields present
        expected_fields = [
            'attribution',
            'totalMatchCount',
            'facetCounts',
            'matches',
            'criteria',
        ]

        assert( TestYummly.verify_fields( expected_fields, results.keys() ) )

        # we got some matches
        assert( len( results['matches'] ) > 0 )

    def test_search_match( self ):
        '''Test search match return'''

        q = 'pork'
        maxResult = 1

        results = self.yummly.search( q, maxResult=maxResult )

        match = results['matches'][0]

        # verify expected fields
        expected_fields = [
            'attributes',
            'flavors',
            'rating',
            'id',
            'smallImageUrls',
            'sourceDisplayName',
            'totalTimeInSeconds',
            'ingredients',
            'recipeName'
        ]

        assert( TestYummly.verify_fields( expected_fields, match.keys() ) )

    def test_search_pagination( self ):
        '''Test search pagination'''

        q = 'fish'
        maxResult = 10

        results = self.yummly.search( q, maxResult=maxResult )

        # verify maxResult enforced
        len_matches = len( results['matches'] )
        assert( len_matches == maxResult )

        # sanity check that grand total of matching recipes is at least as many as matches returned
        assert( results['totalMatchCount'] >= len_matches )

        # check that offsetting works as expected: start is number of records to skip
        start = 5
        offset_results = self.yummly.search( q, maxResult=maxResult, start=start )
        assert( offset_results['matches'][0]['id'] == results['matches'][start]['id'] )

    def test_recipe( self ):
        '''Test fetching recipe data'''
        self.sample_recipe = self.sample_recipe or self.yummly.recipe( self.sample_recipe_id )

        # verify API returns expected fields: https://developer.yummly.com/wiki/get-recipe-response-sample
        expected_fields = [
            'attribution',
            'ingredientLines',
            'flavors',
            'nutritionEstimates',
            'images',
            'name',
            'yield',
            'totalTime',
            'attributes',
            'totalTimeInSeconds',
            'rating',
            'numberOfServings',
            'source',
            'id',
        ]

        # verify we received the expected fields
        assert( TestYummly.verify_fields( expected_fields, self.sample_recipe.keys() ) )

    def test_recipe_nutrition( self ):
        '''Test nutrition fields present in recipe data'''

        self.sample_recipe = self.sample_recipe or self.yummly.recipe( self.sample_recipe_id )

        nutrition = self.sample_recipe['nutritionEstimates'][0]

        expected_fields = [
            'attribute',
            'description',
            'value',
            'unit',
        ]

        assert( TestYummly.verify_fields( expected_fields, nutrition.keys() ) )

        nutrition_unit = nutrition['unit']

        expected_unit_fields = [
            'name',
            'abbreviation',
            'plural',
            'pluralAbbreviation'
        ]

        assert( TestYummly.verify_fields( expected_unit_fields, nutrition_unit.keys() ) )

    def test_recipe_images( self ):
        '''Test image fields present in recipe data'''

        self.sample_recipe = self.sample_recipe or self.yummly.recipe( self.sample_recipe_id )

        images = self.sample_recipe['images'][0]

        expected_fields = [
            'hostedLargeUrl',
            'hostedSmallUrl',
        ]

        assert( TestYummly.verify_fields( expected_fields, images.keys() ) )

    def test_recipe_source( self ):
        '''Test source fields present in recipe data'''

        self.sample_recipe = self.sample_recipe or self.yummly.recipe( self.sample_recipe_id )

        source = self.sample_recipe['source']

        expected_fields = [
            'sourceRecipeUrl',
            'sourceSiteUrl',
            'sourceDisplayName',
        ]

        assert( TestYummly.verify_fields( expected_fields, source.keys() ) )

    def test_recipe_from_search( self ):
        '''Test that recipe fetched from search matches up with search results'''

        q = 'chicken'
        s = self.yummly.search( q, maxResult=1 )

        search = s['matches'][0]
        recipe = self.yummly.recipe( search['id'] )

        # ids should match
        assert( recipe['id'] == search['id'] )

        # both should have same number of ingredients/lines
        assert( len(recipe['ingredientLines']) == len(search['ingredients']) )

        # same prep+cook time
        assert( recipe['totalTimeInSeconds'] == search['totalTimeInSeconds'] )

        # same recipe name
        assert( recipe['name'] == search['recipeName'] )

        # same attributes
        assert( recipe['attributes'] == search['attributes'] )

        # same display name
        assert( recipe['source']['sourceDisplayName'] == search['sourceDisplayName'] )

    def test_search_parameters_basic( self ):
        '''Test basic search parameters received as expected'''

        params = {
            'q':                        'chicken',
            'start':                    0,
            'maxResult':                40,
            'requirePictures':          True,
            'allowedIngredient[]':      ['salt', 'pepper'],
            'excludedIngredient[]':     ['cumin', 'paprika'],
            'maxTotalTimeInSeconds':    60*60, # 1 hour
            'facetField[]':             ['ingredient', 'diet'],
        }

        results = self.yummly.search( **params )

        criteria = results['criteria']

        # verify search terms
        for term in params['q'].split():
            assert( term in criteria['terms'] )

        # verify require pictures
        assert( criteria['requirePictures'] == params['requirePictures'] )

        # verify allowed ingredients
        assert( 'allowedIngredients' in criteria )
        assert( set(criteria['allowedIngredients']) == set(params['allowedIngredient[]']) )

        # verify exluded ingredients
        assert( 'excludedIngredients' in criteria )
        assert( set(criteria['excludedIngredients']) == set(params['excludedIngredient[]']) )

        # verify results are <= max total time
        # @note: this only verifies what's returned so it's possible this value is ignored
        for match in results['matches']:
            assert( match['totalTimeInSeconds'] <= params['maxTotalTimeInSeconds'] )

        # verify facets
        assert( set(criteria['facetFields']) == set(params['facetField[]']) )
        assert( results['facetCounts']['ingredient'] >= 0 )
        assert( results['facetCounts']['diet'] >= 0 )

    def test_search_parameters_flavor( self ):
        '''Test flavor search parameters received as expected'''

        flavors = {
            'sweet': {
                'min': 0,
                'max': 0.75,
            },
            'meaty': {
                'min': 0,
                'max': 1,
            },
            'bitter': {
                'min': 0,
                'max': 0.25,
            },
            'piquant': {
                'min': 0,
                'max': 0.5,
            }
        }

        params = {
            'q':                        'chicken',
            'start':                    0,
            'maxResult':                1,
            'flavor.sweet.min':         flavors['sweet']['min'],
            'flavor.sweet.max':         flavors['sweet']['max'],
            'flavor.meaty.min':         flavors['meaty']['min'],
            'flavor.meaty.max':         flavors['meaty']['max'],
            'flavor.bitter.min':        flavors['bitter']['min'],
            'flavor.bitter.max':        flavors['bitter']['max'],
            'flavor.piquant.min':       flavors['piquant']['min'],
            'flavor.piquant.max':       flavors['piquant']['max'],
        }

        results = self.yummly.search( **params )

        criteria = results['criteria']

        # verify flavors
        attribute_ranges = criteria['attributeRanges']
        for flavor, ranges in flavors.iteritems():
            attr = 'flavor-' + flavor
            assert( attribute_ranges[attr]['min'] == ranges['min'] )
            assert( attribute_ranges[attr]['max'] == ranges['max'] )

    def test_search_parameters_nutrition( self ):
        '''Test nutrition search parameters received as expected'''

        nutrition = {
            'FAT': {
                'min': 0,
                'max': 10,
            },
            'SUGAR': {
                'min': 0,
                'max': 5,
            }
        }

        params = {
            'q':                        'chicken',
            'start':                    0,
            'maxResult':                1,
            'nutrition.FAT.min':        nutrition['FAT']['min'],
            'nutrition.FAT.max':        nutrition['FAT']['max'],
            'nutrition.SUGAR.min':      nutrition['SUGAR']['min'],
            'nutrition.SUGAR.max':      nutrition['SUGAR']['max'],
        }

        results = self.yummly.search( **params )

        criteria = results['criteria']

        # verify nutrition
        nutrition_restrictions = criteria['nutritionRestrictions']
        for nut, ranges in nutrition.iteritems():
            assert( nutrition_restrictions[nut]['min'] == ranges['min'] )
            assert( nutrition_restrictions[nut]['max'] == ranges['max'] )

