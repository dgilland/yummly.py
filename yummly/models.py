
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
    def __init__( self,
        id,
        name,
        ingredientLines,
        source,
        attribution,
        nutritionEstimates=None,
        images=None,
        rating=0,
        flavors=None,
        totalTime=0,
        totalTimeInSeconds=0,
        numberOfServings=0,
        yields='',
        attributes=None,
        ):

        self.id                 = id
        self.name               = name
        self.rating             = rating
        self.totalTime          = totalTime or 0
        self.totalTimeInSeconds = totalTimeInSeconds or 0
        self.ingredientLines    = ingredientLines
        self.numberOfServings   = numberOfServings
        self.yields             = yields or ''
        self.attributes         = attributes or {}

        self.source             = RecipeSource( **source )
        self.attribution        = Attribution( **attribution )

        # @note: for `flavors`, the keys are returned capitalized so normalize to lowercase since search results' flavor keys are lowercase
        flavors = dict( (f.lower(), flavor) for f,flavor in flavors.iteritems() ) if flavors else {}
        self.flavors            = Flavors( **flavors )

        nutritionEstimates      = nutritionEstimates or []
        self.nutritionEstimates = [ NutritionEstimate( **ne ) for ne in nutritionEstimates ]

        images                  = images or []
        self.images             = [ RecipeImages( **imgs ) for imgs in images ]

class Flavors( Storage ):
    def __init__( self, salty=None, meaty=None, piquant=None, bitter=None, sour=None, sweet=None ):
        self.salty      = salty
        self.meaty      = meaty
        self.piquant    = piquant
        self.bitter     = bitter
        self.sour       = sour
        self.sweet      = sweet

class Attribution( Storage ):
    def __init__( self, html, url, text, logo ):
        self.html       = html
        self.url        = url
        self.text       = text
        self.logo       = logo

class NutritionEstimate( Storage ):
    def __init__( self, attribute, description, value, unit ):
        self.attribute      = attribute
        self.description    = description
        self.value          = value
        self.unit           = NutritionUnit( **unit )

class NutritionUnit( Storage ):
    def __init__( self,  id, name, abbreviation, plural, pluralAbbreviation ):
        self.id                 = id
        self.abbreviation       = abbreviation
        self.plural             = plural
        self.pluralAbbreviation = pluralAbbreviation

class RecipeImages( Storage ):
    def __init__( self, hostedLargeUrl, hostedSmallUrl ):
        self.hostedLargeUrl     = hostedLargeUrl
        self.hostedSmallUrl     = hostedSmallUrl

class RecipeSource( Storage ):
    def __init__( self, sourceRecipeUrl, sourceSiteUrl, sourceDisplayName ):
        self.sourceRecipeUrl    = sourceRecipeUrl
        self.sourceSiteUrl      = sourceSiteUrl
        self.sourceDisplayName  = sourceDisplayName

##################################################
# Search related models
##################################################

class SearchResult( Storage ):
    def __init__( self, totalMatchCount, criteria, facetCounts, matches, attribution ):
        self.totalMatchCount    = totalMatchCount
        self.criteria           = SearchCriteria( **criteria )
        self.facetCounts        = facetCounts
        self.matches            = [ SearchMatch( **m ) for m in matches ]
        self.attribution        = Attribution( **attribution )

class SearchMatch( Storage ):
    def __init__( self,
        id,
        recipeName,
        rating,
        ingredients,
        flavors,
        smallImageUrls,
        attributes,
        totalTimeInSeconds=0,
        sourceDisplayName=''
        ):

        self.id                 = id
        self.recipeName         = recipeName
        self.rating             = rating
        self.totalTimeInSeconds = totalTimeInSeconds or 0
        self.ingredients        = ingredients
        self.flavors            = Flavors( **(flavors or {}) )
        self.smallImageUrls     = smallImageUrls
        self.sourceDisplayName  = sourceDisplayName or ''
        self.attributes         = attributes

class SearchCriteria( Storage ):
    def __init__( self,
        maxResults,
        resultsToSkip,
        terms,
        requirePictures,
        facetFields,
        allowedIngredients,
        excludedIngredients,
        attributeRanges=None,
        allowedAttributes=None,
        excludedAttributes=None,
        allowedDiets=None,
        nutritionRestrictions=None
        ):

        self.maxResults             = maxResults
        self.resultsToSkip          = resultsToSkip
        self.terms                  = terms
        self.requirePictures        = requirePictures
        self.facetFields            = facetFields
        self.allowedIngredients     = allowedIngredients
        self.excludedIngredients    = excludedIngredients
        self.attributeRanges        = attributeRanges or {}
        self.allowedAttributes      = allowedAttributes or []
        self.excludedAttributes     = excludedAttributes or []
        self.allowedDiets           = allowedDiets or []
        self.nutritionRestrictions  = nutritionRestrictions or {}

##################################################
# Metadata related models
##################################################

class MetaAttribute( Storage ):
    def __init__( self, id, description, searchValue ):
        self.id             = id
        self.description    = description
        self.searchValue    = searchValue

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

class MetaRestriction( Storage ):
    def __init__( self, id, shortDescription, longDescription, searchValue ):
        self.id                 = id
        self.shortDescription   = shortDescription
        self.longDescription    = longDescription
        self.searchValue        = searchValue

class MetaDiet( MetaRestriction ):
    pass

class MetaAllergy( MetaRestriction ):
    pass

class MetaIngredient( Storage ):
    def __init__( self, id, term, searchValue, ingredientId, useCount ):
        self.id             = id
        self.term           = term
        self.searchValue    = searchValue
        self.ingredientId   = ingredientId
        self.useCount       = useCount

class MetaTechnique( Storage ):
    def __init__( self, id, name, group, searchValue ):
        self.id             = id
        self.name           = name
        self.group          = searchValue

