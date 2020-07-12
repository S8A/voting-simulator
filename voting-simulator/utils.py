# coding=utf-8
"""Utility functions for all modules of the program."""


from itertools import permutations
from textwrap import shorten
from .candidate import Candidate
from .party import Party
from .voter_group import VoterGroup


# Constants

# Example party IDs and names
PARTY_DICT = {
    'I': 'Independent',
    'M': 'Moderate',
    'R': 'Republican',
    'D': 'Democrat',
    'L': 'Libertarian',
    'G': 'Green',
}

# Example parties
PARTIES = parties_from_dict(PARTY_DICT)

# Example voter groups
VOTER_GROUPS = [
    VoterGroup(parties_from_id_list(list('LRMIGD')),
               name='Libertarians'),
    VoterGroup(parties_from_id_list(list('RLMIDG')),
               name='Conservative republicans'),
    VoterGroup(parties_from_id_list(list('RMLIDG')),
               name='Moderate republicans'),
    VoterGroup(parties_from_id_list(list('MRIDLG')),
               name='Right-leaning moderates'),
    VoterGroup(parties_from_id_list(list('MDIRGL')),
               name='Left-leaning moderates'),
    VoterGroup(parties_from_id_list(list('DMGIRL')),
               name='Moderate democrats'),
    VoterGroup(parties_from_id_list(list('DGMIRL')),
               name='Progressive democrats'),
    VoterGroup(parties_from_id_list(list('GDMIRL')),
               name='Greens'),
]


# Functions

def parties_from_dict(party_dict):
    """Generate a list of parties from the given dictionary."""
    return [Party(identifier, name) for identifier, name in party_dict.items()]

def parties_from_id_list(id_list):
    """Generate a list of parties from the given list of party identifiers."""
    parties = []
    for identifier in id_list:
        party = Party(identifier, PARTY_DICT[identifier])
        parties.append(party)
    return parties

def generate_voter_groups():
    """Generate all possible voter groups."""
    party_permutations = list(permutations(PARTIES, len(PARTIES)))
    voter_groups = [VoterGroup(sequence) for sequence in party_permutations]
    return voter_groups

def sort_dict_desc(dictionary):
    """Sorts dictionary in descending order by values."""
    return sorted(dictionary.items(), key=lambda item: item[1], reverse=True)

def make_table(widths, header, body):
    """Makes a text table with the given column widths, header and body."""
    table = [header]
    table.append(['-' * widths[i] for i in range(3)])
    table.extend(body)
    rtable = []
    for i, row in enumerate(table):
        sep = '+' if i == 1 else '|'
        wrow = list(zip(row, widths))
        rtable.append(sep.join([f'{shorten(str(content), w):<{w}}'
                                  for content, w in wrow]))
    return '\n'.join(rtable)

def generate_party_candidates(party, n):
    """Generates a list of n candidates of the given party."""
    return [Candidate(party, i) for i in range(n)]

def generate_candidates(n=0, numbers_for_each={}):
    """Generates a list of candidates of all parties."""
    r = []
    for party in PARTIES.keys():
        number = numbers_for_each.get(party, n)
        r.extend(generate_party_candidates(party, number))
    return r
