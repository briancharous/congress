from base import Chamber, DataManager, VoteRecord

import argparse
import random

from sklearn.cluster import KMeans
from scipy.cluster.vq import kmeans2

class ClusterCongress(object):

    def cluster(self, k):
        clustering = KMeans(n_clusters=k, init='k-means++', verbose=1, random_state=1213, tol=0)
        labels = clustering.fit_predict(self.voting_record.matrix)
        centers = clustering.cluster_centers_
        print(centers)
        print(labels)


    def load_voting_record(self, root_dir, chamber):
        """ get voting record from all files in a root directory (recursive) """
        dataman = DataManager()
        votes, ids = dataman.parse_votes(root_dir, chamber)
        record = VoteRecord(votes, ids)
        self.voting_record = record

    def __init__(self):
        super(ClusterCongress, self).__init__()
        self.voting_record = None

def main():
    c = ClusterCongress()
    c.load_voting_record('.', Chamber.house)
    c.cluster(2)

if __name__ == '__main__':
    main()