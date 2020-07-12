# coding=utf-8
"""Each election result records the voting system used, counts, winners, etc."""


from .utils import sort_dict_desc, make_table


class ElectionResult:

    def __init__(self, voting_system, counts, winners, count_type='Votes',
                 percent_column=True, details=[]):
        """Creates an election result with the given information.
        
        Args:
            voting_system: Name of the voting system used.
            counts: Dictionary mapping candidates to final counts.
            winners: List of winning candidates.
            count_type: Type of count data: Votes, Score, Points, Wins, etc.
            percent_column: Indicates if the results table should have a 
                percent column.
            details: List of text strings with details about the election.
        """
        self.voting_system = voting_system
        self.counts = counts
        self.winners = winners
        self.count_type = count_type
        self.percent_column = percent_column
        self.details = details
    
    def __repr__(self):
        """Returns a string representation of the election result."""
        return f'Election Result ({self.voting_system})'
    
    def summary(self):
        """Returns a summary of the election result.""" 
        summary = [f'Election Result :: {self.voting_system} :.\n']
        summary.extend(self.details)
        summary.append('\nFinal counts:')
        summary.extend(self.counts_table())
        summary.append('\nWinner(s):')
        for winner in self.winners:
            summary.append(str(winner))
        return '\n'.join(summary)
    
    def counts_table(self):
        """Sorts counts and converts them into a text table."""
        widths = [20, 20]
        header = ['Candidate', self.count_type]
        total = sum(list(self.counts.values()))
        sorted_counts = sort_dict_desc(self.counts)
        body = [[candidate, count] for candidate, count in sorted_counts]
        if self.percent_column:
            widths.append(10)
            header.append('Percent')
            for row in body:
                percent = 100.0 * row[1] / total
                row.append(f'{percent :.2f}%')
        return make_table(widths, header, body)
