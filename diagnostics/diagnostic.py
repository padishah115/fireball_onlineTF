#
# DIAGNOSTICS BASE CLASS
#  

class Diagnostic:
    """Parent class for all diagnostics on FIREBALL-III"""

    def __init__(self, name):
        """
        Attributes
        ----------
            name : str
                The name of the diagnostic
        """
        self.name = name