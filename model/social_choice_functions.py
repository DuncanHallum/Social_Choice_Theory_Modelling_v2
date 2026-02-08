"""Defines social choice functions to be used by analysis notebooks"""

import random
import numpy as np
import copy
from typing import Tuple

#Define types
Ballot = Tuple[int, ...]
Profile = Tuple[Ballot, ...]

#Debugging
def validate_profile(profile, n_alts):
    required = set(range(n_alts))
    for idx, b in enumerate(profile):
        if set(b) != required:
            print("BAD BALLOT:", b)
            print("Index in profile:", idx)
            print("Length:", len(b))
            raise ValueError("Invalid ballot detected")

# Plurality Vote
def pluralityVote(profile: Profile, n_alts: int, print_scores=False):
    scores = [0] * n_alts

    for ballot in profile:
        if len(ballot) > 0:
            scores[ballot[0]] += 1

    if print_scores == True:
        print("Plurality scores:",scores)
    max_votes = max(scores)
    return [i for i in range(n_alts) if scores[i] == max_votes]

# Borda Count
def BordaCount(profile: Profile, n_alts: int, print_scores=False):
    scores = [0] * n_alts

    for ballot in profile:
        for rank, alt in enumerate(ballot):
            scores[alt] += n_alts - rank - 1

    if print_scores == True:
        print("Borda scores:",scores)
    max_score = max(scores)
    return [i for i in range(n_alts) if scores[i] == max_score]

# Instant Runnoff Vote, takes paramter print_scores only for consistency
def instantRunoffVote(profile: Profile, n_alts: int, print_scores=False, tie_break_ordering=None):
    # tie_break_vector: defines fixed ordering of alternatives for ties to be broken in (highest to lowest), if None ties are broken randomly
    remaining = set(range(n_alts))
    while True:
        # if only one candidate remains they win
        if len(remaining) == 1:
            return next(iter(remaining))

        totals = {a: 0 for a in remaining}

        # count first non-eliminated preference on each ballot
        for ballot in profile:
            for alt in ballot:
                if alt in remaining:
                    totals[alt] += 1
                    break

        if print_scores:
            print("round totals:", totals)

        max_votes = max(totals.values())

        # majority winner
        if max_votes > len(profile) / 2:
            winners = [a for a,v in totals.items() if v == max_votes]
            return winners if len(winners) > 1 else winners[0]

        # eliminate lowest
        min_votes = min(totals.values())
        losers = [a for a,v in totals.items() if v == min_votes]

        if tie_break_ordering:
            tie_break_ordering = list(reversed(tie_break_ordering)) #use ordering from lowest to highest
            for alt in tie_break_ordering:
                if alt in losers:
                   loser = alt
                   break 
        else:
           loser = random.choice(losers)
        remaining.remove(loser)

# Get Pairwise Majority Matrix (function called by Copeland Rule & used for Condorcet Cycle Analysis notebook)
def getPairMajMat(profile: list[list[int]], n_alts: int, print_scores=False):
    """
    Input: profile, a tuple of tuples of alternatives,
        number of alternatives
    Output: A n_alts*n_alts matrix, where entry i,j represents the number of voters who prefer alternative i over j
    """
    validate_profile(profile, n_alts)
    maj_mat = []

    for i in range(n_alts):
        row = []
        for j in range(n_alts):
            count = 0
            for ballot in profile:
                # assumes full rankings
                if ballot.index(i) < ballot.index(j): #i is preferred over j
                    count += 1
            row.append(count)
        maj_mat.append(row)

    if print_scores:
        print("Majority Matrix: ")
        for row in maj_mat:
            print(row)

    return maj_mat


# Copeland Rule
def CopelandRule(profile: Profile, n_alts: int, print_scores=False):
    maj_mat = getPairMajMat(profile, n_alts, print_scores)
    scores = [0] * n_alts

    for i in range(n_alts):
        for j in range(n_alts):
            if maj_mat[i][j] > maj_mat[j][i]:
                scores[i] += 1
            elif maj_mat[i][j] < maj_mat[j][i]:
                scores[i] -= 1
                
    if print_scores == True:
        print("Copeland scores:",scores)
    max_score = max(scores)
    return [i for i in range(n_alts) if scores[i] == max_score]

# Test
if __name__ == "__main__":
    profile = [
        [0,1,2,3],
        [0,1,2,3],
        [3,1,0,2],
        [3,1,2,0]
    ]

    print("Winners:", instantRunoffVote(profile, len(profile[0]), print_scores=True, tie_break_ordering=[0,1,2,3]))
