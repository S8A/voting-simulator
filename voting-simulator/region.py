# coding=utf-8
"""A voting region is a set of voting districts."""


import random as rd
from .district import VotingDistrict


class VotingDistrictsRegion:

    def __init__(self, name, population, ndistricts, realistic=True):
        """Creates a region with a given population and number of districts."""
        self.name = name
        self.population = population
        self.ndistricts = ndistricts
        self.districts = []
        self.generate_districts(realistic)
    
    def __repr__(self):
        """Generates a string representation of the voting districts region."""
        return (f'{self.name} ({self.population} voters, '
                f'{self.ndistricts} districts)')
    
    def generate_districts(self, realistic):
        """Generates a list of voting districts containing the voters."""
        remaining = self.population
        for i in range(self.ndistricts):
            n = remaining
            if i < self.ndistricts - 1:
                while n >= remaining or n == 0:
                    nmin = round(0.005 * self.population)
                    nmax = round(1.5 * self.population / self.ndistricts)
                    n = rd.randint(nmin, nmax)
            vd = VotingDistrict(f'District {i+1}', n, realistic=realistic)
            self.districts.append(vd)
            remaining -= n
