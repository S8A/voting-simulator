# coding=utf-8
"""A candidate is a member of a party/affiliation identified by a number."""


class Candidate:

    def __init__(self, party, id):
        """Creates a candidate with the given id and party/affiliation.

        Args:
            party: Character representing a party/affiliation.
            id: Unique identifier, preferably an integer.
        """
        self.party = party
        self.id = id

    def __repr__(self):
        """Returns a string representation of the candidate."""
        return f'{PARTIES[self.party]} {self.id}'

    def __eq__(self, other):
        """Check if this candidate is equal to another one or not."""
        if isinstance(other, Candidate):
            return self.party == other.party and self.id == other.id
        return False
