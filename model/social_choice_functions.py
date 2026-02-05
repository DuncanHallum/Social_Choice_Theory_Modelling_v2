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
def pluralityVote(profile: Profile, n_alts: int):
    totals = [0] * n_alts

    for ballot in profile:
        if len(ballot) > 0:
            totals[ballot[0]] += 1

    max_votes = max(totals)
    return [i for i in range(n_alts) if totals[i] == max_votes]

# Borda Count
def BordaCount(profile: Profile, n_alts: int):
    scores = [0] * n_alts

    for ballot in profile:
        for rank, alt in enumerate(ballot):
            scores[alt] += n_alts - rank - 1

    max_score = max(scores)
    return [i for i in range(n_alts) if scores[i] == max_score]

# Instant Runnoff Vote
def instantRunoffVote(profile: Profile, n_alts: int):

    # convert to mutable working copy
    mutable_profile = [list(ballot) for ballot in profile]

    alts_remaining = list(range(n_alts))

    while True:

        # stop if only one left
        if len(alts_remaining) == 1:
            return alts_remaining[0]

        totals = [0] * n_alts

        # plurality count among remaining
        for ballot in mutable_profile:
            while ballot and ballot[0] not in alts_remaining:
                ballot.pop(0)

            if ballot:
                totals[ballot[0]] += 1

        max_votes = max(totals)

        # majority winner
        if max_votes > len(mutable_profile) / 2:
            return totals.index(max_votes)

        # find lowest among remaining
        min_votes = min(totals[a] for a in alts_remaining)
        losers = [a for a in alts_remaining if totals[a] == min_votes]

        loser = random.choice(losers)
        alts_remaining.remove(loser)

        # remove loser from ballots
        for ballot in mutable_profile:
            if loser in ballot:
                ballot.remove(loser)


# Get Pairwise Majority Matrix (function called by Copeland Rule & used for Condorcet Cycle Analysis notebook)
def getPairMajMat(profile: list[list[int]], n_alts: int):
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
                if ballot.index(i) < ballot.index(j):
                    count += 1
            row.append(count)
        maj_mat.append(row)

    return maj_mat


# Copeland Rule
def CopelandRule(profile: Profile, n_alts: int):
    maj_mat = getPairMajMat(profile, n_alts)
    scores = [0] * n_alts

    for i in range(n_alts):
        for j in range(n_alts):
            if maj_mat[i][j] > maj_mat[j][i]:
                scores[i] += 1
            elif maj_mat[i][j] < maj_mat[j][i]:
                scores[i] -= 1

    max_score = max(scores)
    return [i for i in range(n_alts) if scores[i] == max_score]

# Test
profile = [
    [0,1,2,3],
    [1,2,0,3],
    [3,1,0,2]
]

print("Winners:", instantRunoffVote(profile, len(profile[0])))
