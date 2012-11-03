"""
 Basic Objects to deal with environmental data, inspired by Tom Pollard's
 metar parser
"""

def make_float(value):
    """ TODO: make this robust """
    return float(value)

class temperature(object):
    """ A class representing a temperature measure """
    known_units = ['F', 'C', 'K']
    
    def __init__(self, value, units):
        """
        temperature object constructor
        @param value hopefully numeric value
        @param units well formed units 
        """
        self._value = self.make_float(value)
        self._units = units.upper()
    