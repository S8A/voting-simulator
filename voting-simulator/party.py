# coding=utf-8
"""A 'party' is a formal political organization or ideological affiliation."""


class Party:

    def __init__(self, identifier, name):
        """Creates a party with the given identifier and name.

        Args:
            identifier: Unique character or string identifier.
            name: Name of the party.
        """
        self.id = identifier
        self.name = name

    def __repr__(self):
        """Returns a string representation of the party."""
        return self.name

    def __eq__(self, other):
        """Check if this party is equal to another one or not."""
        if isinstance(other, Party):
            return self.id == other.id
        return False
