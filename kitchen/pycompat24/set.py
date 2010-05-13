'''
Importing this module makes sure that a set and frozenset type have been defined
'''
import __builtin__
if not hasattr(__builtin__, 'set'):
    import sets
    __builtin__.set = sets.Set
    __builtin__.frozenset = sets.ImmutableSets
    
