from base import Chamber, DataManager, VoteRecord

import argparse
import random

from sklearn.cluster import KMeans
from scipy.cluster.vq import kmeans2

class ClusterCongress(object):

    def cluster(self, k):
        clustering = KMeans(n_clusters=k, init='k-means++', verbose=0, random_state=1213, tol=0)
        self.cluster_labels = clustering.fit_predict(self.voting_record.matrix)
        self.cluster_centers = clustering.cluster_centers_
        # print(self.cluster_centers)
        # print(self.cluster_labels)

    def check_party_affiliation(self):
        clusters = {}
        for i in range(len(self.cluster_labels)):
            cluster_id = self.cluster_labels[i]
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            voter_id = self.voting_record.row_voter_mappings[i]
            voter = self.members[voter_id]
            clusters[cluster_id].append(voter)
        for cluster in clusters.keys():
            print('Cluster {0}:'.format(cluster))
            for voter in clusters[cluster]:
                print(voter.party)
            print('\n')

    def __init__(self, data_dir, metadata_files, chamber):
        super(ClusterCongress, self).__init__()
        dataman = DataManager()
        record, ids = dataman.parse_votes(data_dir, chamber)
        self.voting_record = VoteRecord(record, ids)
        self.members = dataman.parse_members(metadata_files)

def main():
    c = ClusterCongress('Data', ['Data/legislators-current.csv', 'Data/legislators-historic.csv'], Chamber.senate)
    c.cluster(2)
    c.check_party_affiliation()

if __name__ == '__main__':
    main()