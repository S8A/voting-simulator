# coding=utf-8
"""Utility functions for all modules of the program."""


from textwrap import shorten
from .candidate import Candidate


# Constants

PARTIES = {
    'I': 'Independent',
    'M': 'Moderate',
    'R': 'Republican',
    'D': 'Democrat',
    'L': 'Libertarian',
    'G': 'Green',
}


# Functions

def sort_dict_desc(data):
    """Sorts dict in descending order by values."""
    return sorted(data.items(), key=lambda item: item[1], reverse=True)

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
