'''Samples from GMM with means as positions of parties in political space, then ballot is ranking of closest means from sample'''
import math
import pandas as pd
import numpy as np
from sklearn.mixture import GaussianMixture
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent

N_VOTERS = 10 #100000 # Rough size of Bristol constituency
PARTIES = ["Cons", "Lab", "LibDem", "Green", "Reform"]
EMISSION_DIST = [0.2, 0.23, 0.13, 0.13, 0.31] # from ipsos voting intention opinion poll
PARTY_IDS = [1101, 1102, 1104, 1105, 1106, 1107, 1110]
ELECTION_YEAR = 2024
ATTRIBUTES = ["lrecon", "galtan"]

# GET EMISSION DIST FROM OPINION POLLS, takes opinion poll data for English parties and normalises values (distributing the "other" percentage)
def get_emission_dist(weight_vector):
    n_weights = len(weight_vector)
    total = sum(weight_vector)
    left_over = 1-total
    for i in range(len(weight_vector)):
        weight_vector[i] += left_over/n_weights
    return weight_vector

# GET & CLEAN DATA FRAME
def get_data(BASE_PATH, PARTY_IDS):
    df = pd.read_csv(BASE_PATH/"data"/"1999-2024_CHES_dataset_means.csv")
    df = df[df["year"] == 2024]
    df = df[df["party_id"].isin(PARTY_IDS)]
    return df

# EXTRACT DATA
def get_positions(df, ATTRIBUTES):
    return df[ATTRIBUTES].values

# FIT GMM
def fit_gmm(means, PARTIES, EMISSION_DIST, voter_variance=1.0):
    gmm = GaussianMixture(
        covariance_type='spherical',
        n_components=len(PARTIES),
        random_state=0
    )
    gmm.weights_ = np.array(EMISSION_DIST)
    gmm.means_ = np.array(means)
    # Set spherical variances
    gmm.covariances_ = np.array([voter_variance] * len(PARTIES))
    # Required derived quantity for sklearn sampling
    gmm.precisions_cholesky_ = 1.0 / np.sqrt(gmm.covariances_)
    # Mark as already "fit"
    gmm.converged_ = True
    gmm.n_iter_ = 0
    
    return gmm


# GENERATE SAMPLES
def get_samples(gmm: GaussianMixture, means, n_voters: int, utility):
    parties_and_means = [[i, means[i]] for i in range(len(means))] #party index/id & mean
    sample_points, sample_cluster_labels = gmm.sample(n_samples=n_voters)
    sample_ballots = []

    def distance(point, index_and_mean):
        return math.sqrt((point[0]-index_and_mean[1][0])**2 + (point[1]-index_and_mean[1][1])**2)
        
    for point in sample_points:
        #Sort index and means by euclidean distance from point (ascending by default)
        ranking = sorted(parties_and_means, key=lambda x: distance(point, x))
        #Take just party index/id
        preference_ballot = [x[0] for x in ranking]
        sample_ballots.append(preference_ballot)

    return (sample_points, sample_cluster_labels, sample_ballots)

# RUN CODE
if __name__ == "__main__":
    df = get_data(BASE_PATH, PARTY_IDS)
    means = get_positions(df, ATTRIBUTES)
    gmm = fit_gmm(means, PARTIES, EMISSION_DIST)
    sample_points, sample_cluster_labels, sample_ballots = get_samples(gmm, means, N_VOTERS)
    print(sample_points)
    print(sample_cluster_labels)
    print(sample_ballots)