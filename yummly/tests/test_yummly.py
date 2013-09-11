
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

        cls.yummly = yummly.Client( api_id=config.get('api_id'), api_key=config.get('api_key') )

        cls.sample_recipe_id = 'Hot-Turkey-Salad-Sandwiches-Allrecipes'

    def setUp( self ):
        # wait some time inbetween tests for throttling self
        TestYummly.wait()

    @staticmethod
    def wait(t=1.0):
        sleep(t)

    def test_recipe( self ):
        '''Test fetching recipe data'''
        recipe = self.yummly.recipe( self.sample_recipe_id )

        assert( recipe )

    def test_search( self ):
        '''Test basic search functionality'''

        q = 'chicken casserole'
        maxResult = 5

        results = self.yummly.search( q, maxResult=maxResult )

        # we got some matches
        assert( len( results.matches ) > 0 )

    def test_recipe_from_search( self ):
        '''
        Test that recipe fetched from search matches up with search results
        @note: verifying that a single result isn't sufficient to guarantee this can be done for all search results, nor would it be feasible to do
        @todo: consider dropping this test or expanding results
        '''

        q = 'chicken'
        s = self.yummly.search( q, maxResult=1 )

        search = s.matches[0]
        recipe = self.yummly.recipe( search.id )

        # ids should match
        assert( recipe.id == search.id )

        # both should have same number of ingredients/lines
        assert( len(recipe.ingredientLines) == len(search.ingredients) )

        # same prep+cook time
        assert( recipe.totalTimeInSeconds == search.totalTimeInSeconds )

        # same recipe name
        assert( recipe.name == search.recipeName )

        # same attributes
        assert( recipe.attributes == search.attributes )

        # same display name
        assert( recipe.source.sourceDisplayName == search.sourceDisplayName )

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

        criteria = results.criteria

        # verify search terms
        for term in params['q'].split():
            assert( term in criteria.terms )

        # verify require pictures
        assert( criteria.requirePictures == params['requirePictures'] )

        # verify allowed ingredients
        assert( set(criteria.allowedIngredients) == set(params['allowedIngredient[]']) )

        # verify exluded ingredients
        assert( set(criteria.excludedIngredients) == set(params['excludedIngredient[]']) )

        # verify results are <= max total time
        # @note: this only verifies what's returned so it's possible this value is ignored
        for match in results.matches:
            assert( match.totalTimeInSeconds <= params['maxTotalTimeInSeconds'] )

        # verify facets
        assert( set(criteria.facetFields) == set(params['facetField[]']) )
        assert( results.facetCounts['ingredient'] >= 0 )
        assert( results.facetCounts['diet'] >= 0 )

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

        criteria = results.criteria

        # verify flavors
        attribute_ranges = criteria.attributeRanges
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

        criteria = results.criteria

        # verify nutrition
        nutrition_restrictions = criteria.nutritionRestrictions
        for nut, ranges in nutrition.iteritems():
            assert( nutrition_restrictions[nut]['min'] == ranges['min'] )
            assert( nutrition_restrictions[nut]['max'] == ranges['max'] )

    def test_metadata( self ):
        for key in self.yummly.METADATA:
            data = self.yummly.metadata( key )
            assert( len(data) > 0 )
            TestYummly.wait(0.5)

    def test_metadata_invalid( self ):
        self.assertRaises( yummly.YummlyError, self.yummly.metadata, 'invalid' )

    def test_timeout_retry( self ):
        orig_timeout = self.yummly.timeout
        self.yummly.timeout = 0.01

        retries = 2
        orig_retries = self.yummly.retries
        self.yummly.retries = retries

        self.assertRaises( yummly.Timeout, self.yummly.recipe, self.sample_recipe_id )
        assert( self.yummly._handle_errors_count == retries )

        self.yummly.timeout = orig_timeout
        self.yummly.retries = orig_retries

    def test_missing_total_time( self ):
        # some recipes don't have total time
        # previous versions of yummly.Client didn't handle this properly
        recipe_id   = 'Grilled-Tequila-Lime-Chicken-Once-Upon-A-Chef-200041'
        recipe      = self.yummly.recipe( recipe_id )

        assert( recipe.totalTime == 0 )
        assert( recipe.totalTimeInSeconds == 0 )

    def test_missing_yield( self ):
        # some recipes don't have 'yield' attribute
        recipe_id   = 'Oven-roasted-tomatoes-310681'
        recipe      = self.yummly.recipe( recipe_id )

        assert( recipe.yields == '' )

    def test_missing_images( self ):
        recipe_id   = 'Smoked-Salmon-Food-Network'
        recipe      = self.yummly.recipe( recipe_id )

        for img in recipe.images:
            assert img.hostedLargeUrl is None
            assert img.hostedSmallUrl is None

