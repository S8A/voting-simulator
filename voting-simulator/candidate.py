# coding=utf-8
"""A candidate is a member of a party/affiliation identified by a number."""


class Candidate:

    def __init__(self, party, identifier):
        """Creates a candidate with the given identifier and party/affiliation.

        Args:
            party: Party/affiliation of the candidate.
            identifier: Unique identifier number.
        """
        self.party = party
        self.id = identifier

    def __repr__(self):
        """Returns a string representation of the candidate."""
        return f'{self.party.name} {self.id}'

    def __eq__(self, other):
        """Check if this candidate is equal to another one or not."""
        if isinstance(other, Candidate):
            return self.party == other.party and self.id == other.id
        return False
