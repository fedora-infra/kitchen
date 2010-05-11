'''
Importing this module makes sure that a set and frozenset type have been defined
'''
if not hasattr(__builtin__, 'set'):
    import sets
    set = sets.Set
    frozenset = sets.ImmutableSets
