# coding=utf-8
"""A voting pattern is the preference order of parties of a voter group."""


import itertools as itls
from .utils import PARTIES


class VotingPattern:

    def __init__(self, sequence, name=None):
        """Creates a voting pattern from the given preference order.
        
        Args:
            sequence: List of characters representing different parties.
            name: Optional name of this voter group.
        """
        self.sequence = sequence
        self.name = None if not name else name
    
    def __getitem__(self, key):
        """Gets the item in the given position of the sequence."""
        return self.sequence[key]
    
    def __repr__(self):
        """Returns the string representation of the voting pattern."""
        if not self.name:
            return ''.join(self.sequence)
        else:
            return f'{self.name} ({"".join(self.sequence)})'
    
    def __eq__(self, other):
        """Check if this pattern is equal to another one or not."""
        if isinstance(other, VotingPattern):
            return self.sequence == other.sequence
        return False


ALL_PATTERNS = list(itls.permutations(PARTIES.values(), len(PARTIES.values())))
ALL_PATTERNS = [VotingPattern(seq) for seq in ALL_PATTERNS]

REAL_PATTERNS = [
    VotingPattern(list('LRMIGD'), name='Libertarians'),
    VotingPattern(list('RLMIDG'), name='Conservative republicans'),
    VotingPattern(list('RMLIDG'), name='Moderate republicans'),
    VotingPattern(list('MRIDLG'), name='Right-leaning moderates'),
    VotingPattern(list('MDIRGL'), name='Left-leaning moderates'),
    VotingPattern(list('DMGIRL'), name='Moderate democrats'),
    VotingPattern(list('DGMIRL'), name='Progressive democrats'),
    VotingPattern(list('GDMIRL'), name='Greens'),
]
