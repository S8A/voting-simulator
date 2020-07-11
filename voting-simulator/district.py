# coding=utf-8
"""A district is the voter population of a constituency or geographical area."""


import itertools as itls
import math as m
import random as rd
from .utils import sort_dict_desc
from .candidate import Candidate
from .pattern import VotingPattern, ALL_PATTERNS, REAL_PATTERNS
from .results import VotingResults


class NotEnoughCandidatesError(Exception):
    pass

class InvalidScoreRangeError(Exception):
    pass


class VotingDistrict:

    def __init__(self, name, population, generate=True, realistic=True):
        """Creates a random voting district with the given population size."""
        self.name = name
        self.population = population
        self.pattern_map = {}
        if generate:
            self.pattern_map = self.generate_pattern_map(realistic)
    
    def __repr__(self):
        """Returns a string representation of the voting district."""
        return f'{self.name} ({self.population} voters)'
    
    def generate_pattern_map(self, realistic):
        """Generates a map of voting patterns to percent of population."""
        pattern_map = {}
        remaining = self.population
        possibilities = REAL_PATTERNS if realistic else ALL_PATTERNS
        rd.shuffle(possibilities)
        for i, pattern in enumerate(possibilities):
            n = remaining
            if i < len(possibilities) - 1:
                while n >= remaining:
                    n = rd.randint(0.0, round(0.6 * self.population))
            pattern_map[pattern] = (
                n, round(100.0 * n / self.population, 2))
            remaining -= n
        return pattern_map

    def generate_block_ballots(self, n, candidates, randomize):
        """Generates block voting ballots.

        Each voter group has n available votes, which they fill first with 
        candidates of their preferred party, then from their second preferred 
        party, and so on as needed to fill their ballots. The order of 
        selection may be randomize or not.

        Args:
            n: Number of available votes per ballot.
            candidates: List of candidates. Assumed to be larger than n.
            randomize: If true, the candidates of each party are shuffled 
                before selection when constructing the ballots.

        Returns:
            A list of tuples, containing each voter group's ballot and votes. 
            Each ballot is a list of candidates.
        """
        ballots = []
        # For each voter group (entry in pattern map)
        for pattern, popularity in self.pattern_map.items():
            ballot = []
            votes = popularity[0]
            # Loop through each party in order of preference
            for party in pattern:
                # Stop if there are no votes left
                if len(ballot) >= n:
                    break
                # Get party candidates and shuffle them if required
                choices = [c for c in candidates if c.party == party]
                if randomize:
                    rd.shuffle(choices)
                # Add as many candidates as needed to try to fill the ballot
                ballot.extend(choices[0:n])
            # Add ballot to list
            ballots.append((ballot, votes))
        return ballots
    
    def generate_ranked_ballots(self, n, candidates, randomize):
        """Generates a ranked ballot for each voter group.

        Each voter group chooses and ranks the candidates as follows: the 
        first rank goes to a candidate of their preferred party, the second 
        rank goes to a candidate chosen at random from any of their two most 
        preferred parties, and so on until the ballot is full.

        Args:
            n: Number of ranks per ballot.
            candidates: List of candidates. Assumed to be larger than n.
            randomize: If true, the selection of candidates is randomized on
                each ballot.

        Returns:
            A list of tuples, containing each voter group's ballot and votes. 
            Each ballot is a list of candidates ranked in order of preference.
        """
        ballots = []
        # For each voter group (entry in pattern map)
        for pattern, popularity in self.pattern_map.items():
            votes = popularity[0]
            ranking = []
            # Add candidates to the ballot until it's full
            for k in range(n):
                # Select the first k+1 parties in order of preference
                parties = pattern[0:k+1]
                # Extract a candidate from each party
                # If randomize=True, choose at random
                choices = []
                for p in parties:
                    party_list = [c for c in candidates
                                  if c.party == p and c not in ranking]
                    if randomize:
                        choices.append(rd.choice(party_list))
                    else:
                        choices.append(party_list[0])
                # Select a candidate and add to ranking
                candidate = rd.choice(choices) if randomize else choices[-1]
                ranking.append(candidate)
            # Add finished ballot to list
            ballots.append((ranking, votes))
        return ballots

    def generate_score_ballots(self, n, candidates, min_score, max_score,
                               randomize):
        """Generates a score ballot for each voter group.

        Each voter group gives the maximum score to a candidate of the party 
        they most like, and the minimum score to a candidate of the party they 
        least like. Random scores lower than the maximum are set for other 
        candidates to fill the ballot, but with higher probability of higher 
        scores for candidates of more preferred parties.

        Because the scores of the intermediate candidates are always random, 
        this function does not guarantee reproducibility for n > 2 even if 
        randomize=False, which only affects the selection of the candidates.

        Args:
            n: Number of candidates per ballot. Assumed to be two or more.
            candidates: List of candidates. Assumed to be larger than n.
            min_score: Minimum score of the range.
            max_score: Maximum score of the range. Assumed to be greater than 
                or equal to min_score.
            randomize: If true, the selection of candidates is randomized on 
                each ballot.

        Returns:
            A list of tuples, containing each voter group's ballot and votes. 
            Each ballot is represented as a dictionary mapping a each candidate 
            to its score.
        """
        ballots = []
        # For each voter group (entry in pattern map)
        for pattern, popularity in self.pattern_map.items():
            votes = popularity[0]
            ballot = {}
            # Add candidates to the ballot until it's full
            for k in range(n):
                if k == 0:
                    # Give highest score to a candidate from the voter group's
                    # most-preferred party (MPP)
                    mpp = [c for c in candidates if c.party == pattern[0]]
                    highest_scored = rd.choice(mpp) if randomize else mpp[0]
                    # Add to ballot
                    ballot[highest_scored] = max_score
                elif k == 1:
                    # Give lowest score to a candidate from the voter group's
                    # least-preferred party (LPP)
                    lpp = [c for c in candidates
                           if c.party == pattern[-1] and c not in ballot.keys()]
                    lowest_scored = rd.choice(lpp) if randomize else mpp[0]
                    # Add to ballot
                    ballot[lowest_scored] = min_score
                else:
                    # Select the first k-1 parties in order of preference
                    # Using k-1 instead of k to account for last candidate
                    # already scored
                    parties = pattern[0:k-1]
                    # Extract a candidate from each party
                    # If randomize=True, choose at random
                    choices = []
                    for p in parties:
                        party_list = [
                            c for c in candidates
                            if c.party == p and c not in ballot.keys()]
                        if randomize:
                            choices.append(rd.choice(party_list))
                        else:
                            choices.append(party_list[0])
                    # Select a candidate
                    candidate = rd.choice(choices) if randomize else choices[-1]
                    # Preference factor for the candidate's party
                    party_index = pattern.index(candidate.party)
                    pref_factor = 1 - (party_index / len(pattern))
                    # Choose a random score using a triangular distribution 
                    # and the preference factor to vary the mode
                    mode = round(pref_factor * (max_score - 1))
                    score = rd.triangular(min_score, max_score - 1, mode)
                    # Add to ballot
                    ballot[candidate] = score
            # Add ballot to list
            ballots.append((ballot, votes))
        return ballots

    def simulate_ntv(self, n, seats, candidates, randomize=False):
        """Simulates a generic non-transferable vote.

        This function is a template for multiple non-transferable vote (MNTV), 
        single non-transferable vote (SNTV) and first-past-the-post (FPTP) 
        electoral systems.
        
        This function doesn't account for tactical voting, which may have a 
        huge impact on real life uses of this voting system.

        Args:
            n: Number of available votes per ballot.
            seats: Number of seats to fill.
            candidates: List of candidates.
            randomize: Randomize selection or not.

        Returns:
            A VotingResults object encapsulating the type, results and 
            parameters of the election.
        
        Raises:
            NotEnoughCandidatesError: If the list of candidates is too short.
        """
        if len(candidates) <= 1 or seats > len(candidates):
            raise NotEnoughCandidatesError
        # Generate block vote ballots
        # Each voter group votes in order of party preference
        ballots = self.generate_block_ballots(n, candidates, randomize)
        # Count votes
        results = {c: 0 for c in candidates}
        for ballot, votes in ballots:
            for candidate in ballot:
                results[candidate] += votes
        # The winners are chosen by vote count in descending order,
        # until all seats are filled
        winners = [c for c, v in sort_dict_desc(results)[0:seats]]
        # Prepare results
        name = 'Non-transferable vote (NTV)'
        details = [f'{n} votes per ballot',
                   f'{seats} seats',
                   f'{len(candidates)} candidates']
        if randomize:
            details.append('Randomized ballot generation')
        vr = VotingResults(name, results, winners, details=details)
        return vr
    
    def simulate_sntv(self, seats, candidates, randomize=False):
        """Simulates single non-transferable vote or multi-member plurality.
        
        SNTV is a plurality voting system for multiple seat elections. Each 
        voter votes for a single candidate. If there are n seats to fill, 
        the n candidates with the most votes win.

        This function doesn't account for tactical voting, which may have a 
        huge impact on real life uses of this voting system.

        Args:
            seats: Number of seats to fill.
            candidates: List of candidates.
            randomize: Randomize candidate selection or not.
        
        Returns:
            A VotingResults object encapsulating the type, results and 
            parameters of the election.
        
        Raises:
            NotEnoughCandidatesError: If the list of candidates is too short.
        """
        # Get results: multiple-seat, single-vote NTV
        vr = self.simulate_ntv(1, seats, candidates, randomize=randomize)
        # Change name
        vr.name = 'Single non-transferable vote (SNTV)'
        # Remove votes per ballot line
        del vr.details[0]
        return vr

    def simulate_fptp(self, candidates, randomize=False):
        """Simulates first-past-the-post voting or single-member plurality.
        
        FPTP is a plurality voting system for single seat elections. It's a 
        single-seat version of SNTV: each voter votes for a single candidate, 
        and then the candidate with the most votes in total wins.
        
        This function doesn't account for tactical voting, which may have a 
        huge impact on real life uses of this voting system.

        Args:
            candidates: List of candidates.
            randomize: Randomize selection or not.

        Returns:
            A VotingResults object encapsulating the type, results and 
            parameters of the election.
        
        Raises:
            NotEnoughCandidatesError: If the list of candidates is too short.
        """
        # Get results: single-seat SNTV
        vr = self.simulate_sntv(1, candidates)
        # Change name
        vr.name = 'First-past-the-post (FPTP)'
        # Remove number of seats line
        del vr.details[0]
        return vr
    
    def simulate_mntv(self, seats, candidates, randomize=False):
        """Simulates multiple non-transferable vote or block vote.

        MNTV is a plurality voting system for multiple seat elections. If 
        there are n seats to fill, each voter selects up to n candidates, and 
        then the n candidates with the most votes win.
        
        This function doesn't account for tactical voting, which may have a 
        huge impact on real life uses of this voting system.

        Args:
            seats: Number of seats to fill.
            candidates: List of candidates.
            randomize: Randomize selection or not.

        Returns:
            A VotingResults object encapsulating the type, results and 
            parameters of the election.
        
        Raises:
            NotEnoughCandidatesError: If the list of candidates is too short.
        """
        # Get results: multiple-seat, multiple-vote NTV
        vr = self.simulate_ntv(seats, seats, candidates, randomize=randomize)
        # Change name
        vr.name = 'Multiple non-transferable vote (MNTV)'
        # Remove number of votes line
        del vr.details[0]
        return vr
    
    def simulate_trs(self, candidates, randomize=False):
        """Simulates two-round system or runoff voting.
        
        TRS is a two-round majority voting system for single seat elections. 
        Each voter votes for a single candidate. If any candidate gets a 
        majority of votes on the first round, she's the winner. Otherwise, 
        the two candidates with the most votes move on to the second round. 
        The voters vote again, and the winner is the candidate with the most 
        votes (which must be a majority, because they're only two).

        This implementation makes each voter group vote for a candidate of 
        their preferred party on the first round, and the candidate they prefer 
        the most on the second round. Tactical voting in this system is a lot 
        less intense than in FPTP, but it still exists in real life and it's 
        not accounted for by this function. This function also assumes that 
        each voter group's preferences remain the same between voting rounds, 
        making it equivalent to a contingent vote system.

        Args:
            candidates: List of candidates.
            randomize: Randomize selection or not.

        Returns:
            A VotingResults object encapsulating the type, results and 
            parameters of the election.
        
        Raises:
            NotEnoughCandidatesError: If the list of candidates is too short.
        """
        if len(candidates) <= 1:
            raise NotEnoughCandidatesError
        # Generate single vote ballots
        # Each voter group votes in order of party preference
        ballots = self.generate_block_ballots(1, candidates, randomize)
        # Count votes for the first round
        results = {c: 0 for c in candidates}
        total_votes = 0
        for ballot, votes in ballots:
            candidate = ballot[0]
            results[candidate] += votes
        # Check if a majority was reached
        majority_reached = False
        for candidate, votes in results:
            if votes > 0.5 * total_votes:
                majority_reached = True
                break
        # If there's no majority, move on to the second round
        if not majority_reached:
            # Keep only the top two candidates from the previous round
            a, b = [c for c, v in sort_dict_desc(results)[0:2]]
            # Make each voter group choose the one they prefer
            ballots = self.generate_block_ballots(1, [a, b], randomize)
            # Reset results and count votes 
            results = {a: 0, b: 0}
            for ballot, votes in ballots:
                candidate = ballot[0]
                results[candidate] += votes
        # The winner is the candidate with the majority in the end
        winner = sort_dict_desc(results)[0][0]
        # Prepare results
        name = 'Two-round system (TRS)'
        details = [f'{len(candidates)} initial candidates']
        if randomize:
            details.append('Randomized ballot generation')
        vr = VotingResults(name, results, [winner], details=details)
        return vr
    
    def simulate_stv(self, seats, candidates, droop_quota=True,
                     surplus_transfers=True, randomize=False):
        """Simulates single transferable vote.

        STV is a ranked voting system that approximates proportional 
        representation in multiple seat elections. Each voter ranks the 
        candidates in order of preference (perhaps with a maximum number of 
        rankings). The vote goes to the voter's first preference if possible, 
        but if their first preference is eliminated, instead of being thrown 
        away, the vote is transferred to their next available preference.

        The counting process works thus: votes are totalled, and a quota (the 
        minimum number of votes required to win a seat) is derived. If the 
        voter's first-ranked candidate achieves the quota, the candidate is 
        declared elected; and, in some STV systems, any surplus vote is 
        transferred to other candidates in proportion to the next back-up 
        preference marked on the ballots. If more candidates than seats remain, 
        the candidate with the fewest votes is eliminated, with the votes in 
        their favour being transferred to other candidates as determined by the 
        voters' next back-up preference. These elections and eliminations, and 
        vote transfers if applicable, continue until enough candidates exceed 
        quota to fill all the seats or until there are only as many remaining 
        candidates as there are unfilled seats, at which point the remaining 
        candidates are declared elected.

        Alternatively, there's a simpler method that uses only elimination 
        transfers: sequentially identify the candidate with the least support, 
        eliminate that candidate, and transfer those votes to the next-named 
        candidate on each ballot. This process is repeated until there are 
        only as many candidates left as seats available.

        This function implements the STV process with and without quotas, and 
        with or without surplus transfers. The number of ranks of every ballot 
        is set to be the maximum between 5 and 1.5 times the number of seats 
        to be filled, but never exceeding the number of available candidates.

        Args:
            seats: Number of seats to fill.
            candidates: List of candidates.
            droop_quota: Use the Droop quota or not.
            surplus_transfers: Transfer surplus votes or not.
            randomize: Randomize selection or not.

        Returns:
            A VotingResults object encapsulating the type, results and 
            parameters of the election.
        
        Raises:
            NotEnoughCandidatesError: If the list of candidates is too short.
        """
        if len(candidates) <= 1 or seats > len(candidates):
            raise NotEnoughCandidatesError
        # Ballot size
        n = min(max(round(1.5 * seats), 5), len(candidates))
        # Generate ranked ballots for each voter group
        ballots = self.generate_ranked_ballots(n, candidates, randomize)
        # Count first choices
        results = {c: 0 for c in candidates}
        total_votes = 0
        for ranking, votes in ballots:
            first_choice = ranking[0]
            results[first_choice] +=  votes
            total_votes += votes
        # Calculate quota if required
        quota = None
        if droop_quota:
            quota = m.floor(total_votes / (seats + 1)) + 1
        # Count and transfer votes until all seats are filled
        winners = []
        while len(winners) < seats:
            # Get remaining candidates
            remaining = [(c, v) for c, v in sort_dict_desc(results)
                         if c not in winners and v > 0]
            # If there are two remaining candidates in a single-seat election,
            # mark winner and end process right away, to have more than one 
            # candidate in the results table
            if seats == 1 and len(remaining) == 2:
                winner = remaining[0][0]
                winners.append(winner)
                break
            # If the number of remaining candidates is equal to
            # the number of seats, fill seats and stop the process
            if len(remaining) == seats:
                for candidate, votes in remaining:
                    winners.append(candidate)
                break
            # Check if any remaining candidate reached the quota (if any)
            reached_quota = False
            if droop_quota:
                for candidate, votes in remaining:
                    if votes >= quota:
                        reached_quota = True
                        # Candidate is elected
                        winners.append(candidate)
                        # Remove candidate from the ballots
                        for r, v in ballots:
                            r.remove(candidate)
                        # Remove surplus votes from candidate's vote count
                        surplus = votes - quota
                        results[candidate] -= surplus
                        # If required, transfer surplus votes
                        if surplus_transfers and surplus > 0:
                            # Find the next choice candidate in all ballots
                            # that have this candidate as first choice
                            next_choices = {}
                            for r, v in ballots:
                                if r[0] == candidate:
                                    next_choice = r[1]
                                    next_choices[next_choice] = (
                                        next_choices.get(next_choice, 0) + v)
                            # Distribute surplus evenly among next choices
                            ratio = surplus / votes
                            for c, v in next_choices:
                                new_votes = v * ratio
                                results[c] += m.floor(new_votes)
                                surplus -= new_votes
            # If no candidate reached the quota (or not using it)
            if not reached_quota:
                # Eliminate the least favored candidate (LFC)
                lfc = remaining[-1][0]
                results[lfc] = 0
                # Find the next choice candidate of each voter group that
                # supported the LFC and remove the LFC from each ranking
                next_choices = {}
                for r, v in ballots:
                    if r[0] == lfc:
                        next_choice = r[1]
                        next_choices[next_choice] = (
                            next_choices.get(next_choice, 0) + v)
                    r.remove(lfc)
                # Distribute LFC votes among next choices
                for c, v in next_choices:
                    results[c] += v
                # Remove candidate from the ballots
                for r, v in ballots:
                    r.remove(candidate)    
        # Prepare results
        name = 'Single transferable vote (STV)'
        details = [f'({seats} seats',
                   f'{len(candidates)} candidates',
                   f'{n} ranks per ballot']
        if randomize:
            details.append('Randomized ballot generation')
        if droop_quota:
            method = 'Using Droop quota'
            if surplus_transfers:
                method += ' with surplus transfers'
            else:
                method += ' without surplus transfers'
            details.append(method)
        else:
            details.append('Elimination transfers only')
        vr = VotingResults(name, results, winners, details=details)
        return vr

    def simulate_irv(self, candidates, randomize=False):
        """Simulates instant-runoff voting.

        IRV is a ranked voting system for single seat elections. Each 
        voter ranks the candidates in order of preference (perhaps with a 
        maximum number of rankings). Ballots are initially counted for each 
        voter's top choice. If a candidate has more than half of the vote 
        based on first-choices, that candidate wins. If not, then the 
        candidate with the fewest votes is eliminated. The voters who 
        selected the defeated candidate as a first choice then have their 
        votes added to the totals of their next choice. This process 
        continues until a candidate has more than half of the votes. When 
        the field is reduced to two, it has become an "instant runoff" that 
        allows a comparison of the top two candidates head-to-head.
        
        It's equivalent to a single-seat STV using the eliminations-only 
        method, and this function implements it that way.

        Args:
            candidates: List of candidates.
            randomize: Randomize selection or not.

        Returns:
            A VotingResults object encapsulating the type, results and 
            parameters of the election.
        
        Raises:
            NotEnoughCandidatesError: If the list of candidates is too short.
        """
        # Get results: single-seat, eliminations-only STV
        vr = self.simulate_stv(1, candidates, droop_quota=False,
                               randomize=randomize)
        # Change name
        vr.name = 'Instant-runoff voting (IRV)'
        # Remove number of seats line
        del vr.details[0]
        # Remove method line
        del vr.details[-1]
        return vr
    
    def simulate_copeland(self, candidates, randomize=False):
        """Simulates Copeland's method voting.
        
        Copeland's method is a Smith-efficient Condorcet method for single 
        seat elections. Voters rank the candidates in order of preference in 
        their ballots, and then candidates are ordered by the number of 
        pairwise victories, minus the number of pairwise defeats, according 
        to those ballots.

        When there is no Condorcet winner, this method often leads to ties. 
        For example, if there is a three-candidate majority rule cycle, each 
        candidate will have exactly one loss, and there will be an unresolved 
        tie between the three.

        In this implementation, the number of ranks of every ballot is set to 
        be a random number between 5 and 10, but never exceeding the number 
        of available candidates.

        Args:
            candidates: List of candidates.
            randomize: Randomize selection or not.

        Returns:
            A VotingResults object encapsulating the type, results and 
            parameters of the election.
        
        Raises:
            NotEnoughCandidatesError: If the list of candidates is too short.
        """
        if len(candidates) <= 1:
            raise NotEnoughCandidatesError
        # Ballot size
        n = min(rd.randint(5, 10), len(candidates))
        # Generate ranked ballots for each voter group
        ballots = self.generate_ranked_ballots(n, candidates, randomize)
        # List all ranked candidates
        ranked_candidates = []
        for ranking, votes in ballots:
            for candidate in ranking:
                if candidate not in ranked_candidates:
                    ranked_candidates.append(candidate)
        # Generate pairwise matchings
        matchings = list(itls.combinations(ranked_candidates, 2))
        # Get results of each pairwise matching
        won = {c: 0 for c in ranked_candidates}
        lost = {c: 0 for c in ranked_candidates}
        for a, b in matchings:
            votes = {a: 0, b: 0}
            # Loop through each ballot
            for ranking, votes in ballots:
                # Check which candidate is preferred and increase its 
                # vote count. There are no ties in any ranking.
                if ranking.index(a) < ranking.index(b):
                    votes[a] += votes
                else:
                    votes[b] += votes
            # Update win/loss counts
            if votes[a] > votes[b]:
                won[a] += 1
                lost[b] += 1
            elif votes[a] < votes[b]:
                won[b] += 1
                lost[a] += 1
        # The winner is the candidate with the highest win-loss score
        win_loss = {c: won[c] - lost[c] for c in ranked_candidates}
        winner = sort_dict_desc(win_loss)[0][0]
        # Prepare results
        name = 'Copeland\'s method'
        details = [f'{len(candidates)} candidates',
                   f'{n} ranks per ballot']
        vr = VotingResults(name, win_loss, [winner], count_type='Win-loss',
                           percent_column=False, details=details)
        return vr

    def simulate_borda_count(self, candidates, variant='standard',
                             randomize=False):
        """Simulates Borda count voting.
        
        The Borda count is a family of ranked voting systems for single seat 
        elections. Each voter ranks the candidates by order of preference and, 
        for each ballot, the candidates are given points according to their 
        rank position.
        
        In the standard Borda count, if there are n candidates, the first 
        rank awards n points, the second n-1 points, and so on. A "zero-index" 
        version of the same scheme can be created by starting at n-1 points 
        for the first candidate. There's also a variant called Dowdall system, 
        where the first rank awards 1 point, the second 1/2 point, the third 
        1/3, and so on, making the scores independent from the number of 
        candidates.

        This function implements all three variants: standard Borda count, 
        zero-index variant, and Dowdall system. The number of ranks of every 
        ballot is set to be a random number between 5 and 10, but never 
        exceeding the number of available candidates.

        Args:
            candidates: List of candidates.
            variant: Variant of Borda count to use. Choices are 'standard',
                'zero-index', or 'dowdall'.
            randomize: Randomize selection or not.

        Returns:
            A VotingResults object encapsulating the type, results and 
            parameters of the election.
        
        Raises:
            NotEnoughCandidatesError: If the list of candidates is too short.
        """
        if len(candidates) <= 1:
            raise NotEnoughCandidatesError
        # Ballot size
        n = min(rd.randint(5, 10), len(candidates))
        # Generate ranked ballots for each voter group
        ballots = self.generate_ranked_ballots(n, candidates, randomize)
        # Score the candidates in each ballot
        scores = {c: 0 for c in candidates}
        for ranking, votes in ballots:
            for i, candidate in enumerate(ranking):
                # Score must be multiplied by the amount of votes
                score = votes
                if variant == 'dowdall':
                    # Dowdal system: Score declines harmonically
                    # according to sequence position
                    score *= (1.0 / (i + 1))
                else:
                    # Standard/zero-index: Score declines arithmetically
                    # according to sequence position
                    score *= n - i - 1 if variant == 'zero-index' else n - i
                scores[candidate] += round(score)
        # The winner is the candidate with the highest score
        winner = sort_dict_desc(scores)[0][0]
        # Prepare results
        name = 'Borda count'
        details = []
        if variant == 'dowdall':
            details.append('Dowdall system')
        elif variant == 'zero_index':
            details.append('Zero-index variant')
        details.extend([f'{len(candidates)} candidates',
                        f'{n} ranks per ballot'])
        if randomize:
            details.append('Randomized ballot generation')
        vr = VotingResults(name, scores, [winner], count_type='Score',
                           details=details)
        return vr

    def simulate_bucklin_voting(self, candidates, randomize=False):
        """Simulates Bucklin voting.
        
        Bucklin voting is a family of ranked voting systems for single seat 
        elections. In the standard process, each voter ranks the candidates 
        by order of preference and first choice votes are counted. If a 
        candidate has a majority, that candidate wins. Otherwise, second 
        choices are added to the first choices. If a candidate has a majority, 
        that candidate wins, or the process continues until a majority is 
        reached.

        This function implements the standard Bucklin voting procedure. The 
        number of ranks of every ballot is set to be a random number between 
        5 and 10, but never exceeding the number of available candidates.

        Args:
            candidates: List of candidates.
            randomize: Randomize selection or not.

        Returns:
            A VotingResults object encapsulating the type, results and 
            parameters of the election.
        
        Raises:
            NotEnoughCandidatesError: If the list of candidates is too short.
        """
        if len(candidates) <= 1:
            raise NotEnoughCandidatesError
        # Ballot size
        n = min(rd.randint(5, 10), len(candidates))
        # Generate ranked ballots for each voter group
        ballots = self.generate_ranked_ballots(n, candidates, randomize)
        # Count the votes on each round
        total_votes = sum([v for r, v in ballots])
        results = {c: 0 for c in candidates}
        while True:
            # Loop through ballots
            for ranking, votes in ballots:
                # If there are no candidates left in the ranking, move on
                if not ranking:
                    continue
                # Add votes to remaining first choice
                candidate = ranking[0]
                results[candidate] += votes
                # Remove this choice from the ranking
                del ranking[0]
            # Check if a majority was reached
            majority_reached = False
            for candidate, votes in results:
                if votes > 0.5 * total_votes:
                    majority_reached = True
                    break
            # If so, end the process
            if majority_reached:
                break
        # The winner is the candidate with the most votes
        winner = sort_dict_desc(results)[0][0]
        # Prepare results
        name = 'Bucklin voting'
        details = [f'{len(candidates)} candidates',
                   f'{n} ranks per ballot']
        if randomize:
            details.append('Randomized ballot generation')
        vr = VotingResults(name, results, [winner], details=details)
        return vr
    
    def simulate_score_voting(self, candidates, min_score, max_score,
                              randomize=False):
        """Simulates score voting or range voting.

        Score voting is a family of cardinal voting systems for single seat 
        elections. In the standard process, each voter gives each candidate a 
        score, the scores are then summed, and the winner is the one with the 
        highest total score.

        In this implementation, the number of ranks of every ballot is set to 
        be a random number between 5 and 10, but never exceeding the number 
        of available candidates.

        This function has zero guarantee of reproducibility, since the 
        scoring process is completely randomized for all but the highest- and 
        lowest-ranked candidates on each ballot.

        Args:
            candidates: List of candidates
            min_score: Minimum score of the range
            max_score: Maximum score of the range
            randomize: Randomize selection or not.

        Returns:
            A VotingResults object encapsulating the type, results and 
            parameters of the election.
        
        Raises:
            NotEnoughCandidatesError: If the list of candidates is too short.
            InvalidScoreRangeError: If the given minimum score is greater 
                than the maximum
        """
        if len(candidates) <= 1:
            raise NotEnoughCandidatesError
        if min_score > max_score:
            raise InvalidScoreRangeError
        # Ballot size
        n = min(rd.randint(5, 10), len(candidates))
        # Generate score ballots
        ballots = self.generate_score_ballots(
            n, candidates, min_score, max_score, randomize)
        # Count the scores for each candidate
        results = {c: 0 for c in candidates}
        for ballot, votes in ballots:
            for candidate, score in ballot.items():
                results[candidate] += votes * score
        # The winner is the candidate with the highest score
        winner = sort_dict_desc(results)[0][0]
        # Prepare results
        name = 'Score voting'
        details = [f'Score range [{min_score}, {max_score}]',
                   f'{len(candidates)} candidates',
                   f'{n} ranks per ballot',
                   'Randomized selection']
        vr = VotingResults(name, results, [winner], count_type='Score', 
                           percent_column=False, details=details)
        return vr

    def simulate_cav(self, candidates, randomize=False):
        """Simulates combined approval voting or evaluative voting.
        
        CAV is a type of score voting system for single seat elections, 
        where each voter may express approval (1), disapproval (0), or 
        indifference (-1) toward each candidate, then the scores are summed 
        and the winner is the most-approved candidate (highest score).

        This function has zero guarantee of reproducibility, since the 
        scoring process is completely randomized for all but the highest- and 
        lowest-ranked candidates on each ballot.

        Args:
            candidates: List of candidates
            randomize: Randomize selection or not.

        Returns:
            A VotingResults object encapsulating the type, results and 
            parameters of the election.
        
        Raises:
            NotEnoughCandidatesError: If the list of candidates is too short.
        """
        # Get results: score voting with score range [-1, 1]
        vr = self.simulate_score_voting(candidates, -1, 1, randomize=randomize)
        # Change name
        vr.name = 'Combined approval voting (CAV)'
        # Change score range line
        vr.details[0] = 'Scores used: support (1), neutral (0), oppose (-1)'
        return vr
    
    def simulate_approval_voting(self, candidates, randomize=False):
        """Simulates approval voting.

        Approval voting is a type of score voting system for single seat 
        elections, where each voter may approve (1) or not (0) any number of 
        candidates, and the winner is the most-approved candidate.

        This function has zero guarantee of reproducibility, since the 
        scoring process is completely randomized for all but the highest- and 
        lowest-ranked candidates on each ballot.

        Args:
            candidates: List of candidates
            randomize: Randomize selection or not.

        Returns:
            A VotingResults object encapsulating the type, results and 
            parameters of the election.
        
        Raises:
            NotEnoughCandidatesError: If the list of candidates is too short.
        """
        # Get results: score voting with score range [0, 1]
        vr = self.simulate_score_voting(candidates, 0, 1, randomize=randomize)
        # Change name
        vr.name = 'Approval voting'
        # Change results count type
        vr.count_type = 'Approvals'
        # Change score range line
        vr.details[0] = 'Each approval counts as one point'
        return vr
    
    def simulate_star_bloc_voting(self, seats, candidates, randomize=False):
        """Simulates score-then-automatic-runoff (STAR) bloc voting.

        START bloc voting is an adaptation of the STAR voting system for 
        multiple seat elections. Each voter scores all the candidates on 
        a scale from 0 to 5. All the scores are added and the two highest 
        scoring candidates advance to an automatic runoff. The finalist who 
        was preferred by (scored higher by) more voters wins the first seat. 
        The next two highest scoring candidates then runoff, with the finalist 
        preferred by more voters winning the next seat. This process continues 
        until all positions are filled.

        This function has zero guarantee of reproducibility, since the 
        scoring process is completely randomized for all but the highest- and 
        lowest-ranked candidates on each ballot.

        Args:
            seats: Number of seats to be filled
            candidates: List of candidates
        
        Returns:
            A VotingResults object encapsulating the type, results and 
            parameters of the election.
        
        Raises:
            NotEnoughCandidatesError: If the list of candidates is too short.
        """
        if len(candidates) <= 1 or seats > len(candidates):
            raise NotEnoughCandidatesError
        # Ballot size
        n = min(rd.randint(5, 10), len(candidates))
        # Generate score ballots
        ballots = self.generate_score_ballots(n, candidates, 0, 5, randomize)
        # Count the scores for each candidate
        results = {c: 0 for c in candidates}
        for ballot, votes in ballots:
            for candidate, score in ballot:
                results[candidate] += votes * score
        # Fill the seats
        winners = []
        while len(winners) < seats:
            # Get remaining candidates
            remaining = [(c, v) for c, v in sort_dict_desc(results)
                         if c not in winners and v > 0]
            # If the number of remaining candidates is equal to
            # the number of seats, fill seats and stop the process
            if len(remaining) == seats:
                for candidate, votes in remaining:
                    winners.append(candidate)
                break
            # Automatic runoff with the two two candidates
            a, b = [c for c, v in remaining[0:2]]
            runoff = {a: 0, b: 0}
            for ballot, votes in ballots:
                # Get highest score of each candidate
                max_a = max([s for c, s in ballot if c == a])
                max_b = max([s for c, s in ballot if c == b])
                # Compare highest scores
                if max_a < max_b:
                    # Prefers candidate B
                    runoff[b] += votes
                elif max_a > max_b:
                    # Prefers candidate B
                    runoff[a] += votes
            # The candidate with the highest runoff score wins a seat
            winner = sort_dict_desc(runoff)[0][0]
            winners.append(winner)
        # Prepare results
        name = 'Score-then-automatic-runoff (STAR) bloc voting'
        details = [f'{seats} seats',
                   f'{len(candidates)} candidates',
                   f'{n} ranks per ballot',
                   'Randomized selection']
        vr = VotingResults(name, results, winners, details=details)
        return vr
    
    def simulate_star_voting(self, candidates, randomize=False):
        """Simulates score-then-automatic-runoff (STAR) voting.

        START voting is a voting system for single seat elections that consists 
        of score voting and a virtual runoff. Each voter scores all the 
        candidates on a scale from 0 to 5. All the scores are added and the two 
        highest scoring candidates advance to an automatic runoff. The finalist 
        who was preferred by (scored higher by) more voters wins.

        This function has zero guarantee of reproducibility, since the 
        scoring process is completely randomized for all but the highest- and 
        lowest-ranked candidates on each ballot.

        Args:
            candidates: List of candidates
        
        Returns:
            A VotingResults object encapsulating the type, results and 
            parameters of the election.
        
        Raises:
            NotEnoughCandidatesError: If the list of candidates is too short.
        """
        # Get results: single-seat STAR bloc voting
        vr = self.simulate_star_bloc_voting(1, candidates, randomize=randomize)
        # Change name
        vr.name = 'Score-then-automatic-runoff (STAR) voting'
        # Remove number of seats line
        del vr.details[0]
        return vr


