# coding=utf-8
"""Each voter group has a particular preference order of parties."""


import itertools as itls
from .party import Party


class VoterGroup:

    def __init__(self, preferences, name=''):
        """Creates a voter group with a given preference order.
        
        Args:
            preferences: List of parties in order of preference.
            name: Optional name for this voter group.
        """
        self.preferences = preferences
        self.name = name
    
    def __repr__(self):
        """Returns a string representation of the voter group."""
        if self.name:
            return self.name
        else:
            party_ids = [party.id for party in self.preferences]
            return f'Voter Group ({", ".join(party_ids)})'
    
    def __eq__(self, other):
        """Check if this voter group is equal to another one or not."""
        if isinstance(other, VoterGroup):
            return self.preferences == other.preferences
        return False
