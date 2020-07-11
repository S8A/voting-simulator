# coding=utf-8
"""A voting results encapsulates the results and other data of an election."""


from .utils import sort_dict_desc, make_table


class VotingResults:

    def __init__(self, name, results, winners, count_type='Votes',
                 percent_column=True, details=[]):
        """Creates a voting results objetc with the given information.
        
        Args:
            name: Name of the election/results.
            results: Dictionary mapping candidates to counts.
            winners: List of winning candidates.
            count_type: Type of count data: Votes, Score, Points, etc.
            percent_column: Indicates if the results table should have a 
                percent column.
            details: List of text strings with details about the election.
        """
        self.name = name
        self.results = results
        self.winners = winners
        self.count_type = count_type
        self.percent_column = percent_column
        self.details = details
    
    def __repr__(self):
        """Returns a string representation fo the voting results."""
        r = [f'Results : {self.name} ::..\n']
        r.extend(self.details)
        r.append('\n')
        r.extend(self.results_table())
        r.append('\nWinner(s):')
        for winner in self.winners:
            r.append(str(winner))
        return '\n'.join(r)
    
    def results_table(self):
        """Sorts results and converts them into a table."""
        widths = [20, 20]
        header = ['Candidate', self.count_type]
        total = sum(list(self.results.values()))
        sorted_results = sort_dict_desc(self.results)
        body = [[candidate, count] for candidate, count in sorted_results]
        if self.percent_column:
            widths.append(10)
            header.append('Percent')
            for row in body:
                percent = 100.0 * row[1] / total
                row.append(f'{percent:.2f}%')
        return make_table(widths, header, body)
