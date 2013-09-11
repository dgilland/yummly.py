
from inspect import getargspec

class Storage( dict ):
    '''
    An object that is like a dict except `obj.foo` can be used in addition to `obj['foo']`.

    Raises Attribute/Key errors for missing references.

    >>> o = Storage(a=1, b=2)

    >>> assert( o.a == o['a'] )
    >>> assert( o.b == o['b'] )

    >>> o.a = 2
    >>> print o['a']
    2

    >>> x = o.copy()
    >>> assert(x == o)

    >>> del o.a
    >>> print o.a
    Traceback (most recent call last):
    ...
    AttributeError: a

    >>> print o['a']
    Traceback (most recent call last):
    ...
    KeyError: 'a'

    >>> o._get_fields()
    Traceback (most recent call last):
    ...
    TypeError: <slot wrapper '__init__' of 'dict' objects> is not a Python function

    '''

    def __getattr__(self, key):
        if key in self:
            return self[key]
        else:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        if key in self:
            del self[key]
        else:
            raise AttributeError(key)

    def __repr__(self):
		return '%s(%s)' % ( self.__class__.__name__, dict.__repr__(self) )

    @classmethod
    def _get_fields( cls ):
        '''
        Return class' __init__() args excluding `self`
        Assumes that calling class has actually implemented __init__(), otherwise, this will fail
        '''
        # for classes, first element of args == self which we don't want
        return getargspec( cls.__init__ ).args[1:]

##################################################
# Get recipe related models
##################################################

# @note: use `Recipe.yields` instead of API `yield` since `yield` is a keyword
class Recipe( Storage ):
    def __init__( self, **kargs ):

        self.id                 = kargs['id']
        self.name               = kargs['name']
        self.rating             = kargs.get('rating')
        self.totalTime          = kargs.get('totalTime') or 0
        self.totalTimeInSeconds = kargs.get('totalTimeInSeconds') or 0
        self.ingredientLines    = kargs.get('ingredientLines') or  []
        self.numberOfServings   = kargs.get('numberOfServings')
        self.yields             = kargs.get('yields')
        self.attributes         = kargs.get('attributes') or {}

        self.source             = RecipeSource( **(kargs.get('source') or {}) )
        self.attribution        = Attribution( **(kargs.get('attribution') or {}) )

        # @note: for `flavors`, the keys are returned capitalized so normalize to lowercase since search results' flavor keys are lowercase
        flavors                 = kargs.get('flavors') or {}
        self.flavors            = Flavors( **{ f.lower(): flavor for f,flavor in flavors.iteritems() } )

        self.nutritionEstimates = [ NutritionEstimate( **ne ) for ne in (kargs.get('nutritionEstimates') or []) ]

        self.images             = [ RecipeImages( **imgs ) for imgs in (kargs.get('images') or []) ]

class Flavors( Storage ):
    def __init__( self, **kargs ):
        self.salty      = kargs.get('salty')
        self.meaty      = kargs.get('meaty')
        self.piquant    = kargs.get('piquant')
        self.bitter     = kargs.get('bitter')
        self.sour       = kargs.get('sour')
        self.sweet      = kargs.get('sweet')

class Attribution( Storage ):
    def __init__( self, **kargs ):
        self.html       = kargs.get('html')
        self.url        = kargs.get('url')
        self.text       = kargs.get('text')
        self.logo       = kargs.get('logo')

class NutritionEstimate( Storage ):
    def __init__( self, **kargs ):
        self.attribute      = kargs.get('attribute')
        self.description    = kargs.get('description')
        self.value          = kargs.get('value')
        self.unit           = NutritionUnit( **(kargs.get('unit') or {}) )

class NutritionUnit( Storage ):
    def __init__( self, **kargs ):
        self.id                 = kargs['id']
        self.abbreviation       = kargs.get('abbreviation')
        self.plural             = kargs.get('plural')
        self.pluralAbbreviation = kargs.get('pluralAbbreviation')

class RecipeImages( Storage ):
    def __init__( self, **kargs ):
        self.hostedLargeUrl     = kargs.get('hostedLargeUrl')
        self.hostedSmallUrl     = kargs.get('hostedSmallUrl')

class RecipeSource( Storage ):
    def __init__( self, **kargs ):
        self.sourceRecipeUrl    = kargs.get('sourceRecipeUrl')
        self.sourceSiteUrl      = kargs.get('sourceSiteUrl')
        self.sourceDisplayName  = kargs.get('sourceDisplayName')

##################################################
# Search related models
##################################################

class SearchResult( Storage ):
    def __init__( self, **kargs ):
        self.totalMatchCount    = kargs['totalMatchCount']
        self.criteria           = SearchCriteria( **kargs['criteria'] )
        self.facetCounts        = kargs['facetCounts']
        self.matches            = [ SearchMatch( **m ) for m in kargs['matches'] ]
        self.attribution        = Attribution( **kargs['attribution'] )

class SearchMatch( Storage ):
    def __init__( self, **kargs ):

        self.id                 = kargs['id']
        self.recipeName         = kargs['recipeName']
        self.rating             = kargs.get('rating')
        self.totalTimeInSeconds = kargs.get('totalTimeInSeconds', 0)
        self.ingredients        = kargs.get('ingredients')
        self.flavors            = Flavors( **(kargs.get('flavors') or {}) )
        self.smallImageUrls     = kargs.get('smallImageUrls')
        self.sourceDisplayName  = kargs.get('sourceDisplayName', '')
        self.attributes         = kargs.get('attributes')

class SearchCriteria( Storage ):
    def __init__( self, **kargs ):

        self.maxResults             = kargs.get('maxResults')
        self.resultsToSkip          = kargs.get('resultsToSkip')
        self.terms                  = kargs.get('terms')
        self.requirePictures        = kargs.get('requirePictures')
        self.facetFields            = kargs.get('facetFields')
        self.allowedIngredients     = kargs.get('allowedIngredients')
        self.excludedIngredients    = kargs.get('excludedIngredients')
        self.attributeRanges        = kargs.get('attributeRanges', {})
        self.allowedAttributes      = kargs.get('allowedAttributes', [])
        self.excludedAttributes     = kargs.get('excludedAttributes', [])
        self.allowedDiets           = kargs.get('allowedDiets', [])
        self.nutritionRestrictions  = kargs.get('nutritionRestrictions', {})

##################################################
# Metadata related models
##################################################

class MetaAttribute( Storage ):
    def __init__( self, **kargs ):
        self.id             = kargs['id']
        self.description    = kargs['description']
        self.searchValue    = kargs['searchValue']

class MetaHoliday( MetaAttribute ):
    pass

class MetaCuisine( MetaAttribute ):
    pass

class MetaCourse( MetaAttribute ):
    pass

class MetaSource( MetaAttribute ):
    pass

class MetaBrand( MetaAttribute ):
    pass

class MetaTechnique( MetaAttribute ):
    pass

class MetaRestriction( Storage ):
    def __init__( self, **kargs ):
        self.id                 = kargs['id']
        self.shortDescription   = kargs['shortDescription']
        self.longDescription    = kargs['longDescription']
        self.searchValue        = kargs['searchValue']

class MetaDiet( MetaRestriction ):
    pass

class MetaAllergy( MetaRestriction ):
    pass

class MetaIngredient( Storage ):
    def __init__( self, **kargs ):
        self.id             = kargs['id']
        self.term           = kargs['term']
        self.searchValue    = kargs['searchValue']
        self.ingredientId   = kargs['ingredientId']
        self.useCount       = kargs['useCount']

