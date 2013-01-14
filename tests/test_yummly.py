
import os

import unittest
import json

import yummly

HERE = os.path.dirname(__file__)

class TestYummly( unittest.TestCase ):

    def setUp( self ):
        config_file = os.path.join( HERE, 'config.json' )

        with open( config_file ) as f:
            config = json.load(f)

        self.yummly = yummly
        self.yummly.api_id  = config.get('api_id')
        self.yummly.api_key = config.get('api_key')

        self.test_recipe_id = 'Hot-Turkey-Salad-Sandwiches-Allrecipes'
        # cache recipe results to decrease API hits
        self.test_recipe = None

    @staticmethod
    def verify_fields( expected, actual ):
        for field in expected:
            assert( field in actual )

        return True

    def test_search( self ):
        '''Test basic search functionality'''

        q       = 'chicken casserole'
        limit   = 5

        results = self.yummly.search( q, limit=limit )

        # verify fields present
        expected_fields = [
            'attribution',
            'totalMatchCount',
            'facetCounts',
            'matches',
            'criteria',
        ]

        assert( TestYummly.verify_fields( expected_fields, results.keys() ) )

        # sanity check that our search terms are included
        for term in q.split():
            assert( term in results['criteria']['terms'] )

        # we got some matches
        assert( len( results['matches'] ) > 0 )

    def test_search_match( self ):
        '''Test search match return'''
        q       = 'chicken'
        limit   = 1

        results = self.yummly.search( q, limit=limit )

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

        q       = 'chicken casserole'
        limit   = 10

        results = self.yummly.search( q, limit=limit )

        # verify limit enforced
        len_matches = len( results['matches'] )
        assert( len_matches == limit )

        # sanity check that grand total of matching recipes is at least as many as matches returned
        assert( results['totalMatchCount'] >= len_matches )

        # check that offsetting works as expected: offset is number of records to skip
        offset = 5
        offset_results = self.yummly.search( q, limit=limit, offset=offset )
        assert( offset_results['matches'][0]['id'] == results['matches'][offset]['id'] )

    def test_recipe( self ):
        self.test_recipe = self.test_recipe or self.yummly.recipe( self.test_recipe_id )

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
        assert( TestYummly.verify_fields( expected_fields, self.test_recipe.keys() ) )

    def test_recipe_nutrition( self ):
        self.test_recipe = self.test_recipe or self.yummly.recipe( self.test_recipe_id )

        nutrition = self.test_recipe['nutritionEstimates'][0]

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
        self.test_recipe = self.test_recipe or self.yummly.recipe( self.test_recipe_id )

        images = self.test_recipe['images'][0]

        expected_fields = [
            'hostedLargeUrl',
            'hostedSmallUrl',
        ]

        assert( TestYummly.verify_fields( expected_fields, images.keys() ) )

    def test_recipe_source( self ):
        self.test_recipe = self.test_recipe or self.yummly.recipe( self.test_recipe_id )

        source = self.test_recipe['source']

        expected_fields = [
            'sourceRecipeUrl',
            'sourceSiteUrl',
            'sourceDisplayName',
        ]

        assert( TestYummly.verify_fields( expected_fields, source.keys() ) )

    def test_recipe_from_search( self ):
        q = 'chicken'
        s = self.yummly.search( q, limit=1 )

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

