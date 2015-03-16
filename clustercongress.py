from base import Chamber, DataManager, VoteRecord

import argparse
import csv
import os
import random
import sys

from sklearn.cluster import KMeans

class ClusterCongress(object):

    def cluster(self, k):
        clustering = KMeans(n_clusters=k, init='k-means++', verbose=0, random_state=1213, tol=0)
        self.cluster_labels = clustering.fit_predict(self.voting_record.matrix)
        self.cluster_centers = clustering.cluster_centers_

    def check_party_affiliation(self):
        # get a dict of each cluster with congressperson
        clusters = {}
        for i in range(len(self.cluster_labels)):
            cluster_id = self.cluster_labels[i]
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            voter_id = self.voting_record.row_voter_mappings[i]
            if voter_id in self.members:
                voter = self.members[voter_id]
                clusters[cluster_id].append(voter)
            else:
                print("WARNING: Voter ID {0} encountered in voting record but representative not found".format(voter_id))

        # get party affilication for each member in the cluster, count the # of party members in each cluster
        cluster_counts = {}
        for cluster in clusters.keys():
            cluster_counts[cluster] = {}
            if self.verbose:
                print('Cluster {0}:'.format(cluster))
            for voter in clusters[cluster]:
                party_counts = cluster_counts[cluster]
                if voter.party not in party_counts:
                    party_counts[voter.party] = 0
                party_counts[voter.party] += 1
                if self.verbose:
                    print('{2}: {0} {1}, {3}'.format(voter.first_name, voter.last_name, voter.party, voter.state))
            if self.verbose:
                print('\n')

        return self.partisanship(cluster_counts)

    def partisanship(self, cluster_counts):
        """ function of how "partisan" each congress was. sum from 1 to n: 1/n * largest group in cluster's percentage """
        party_percents = []
        for cluster in cluster_counts:
            total_members = 0
            for party in cluster_counts[cluster]:
                total_members += cluster_counts[cluster][party]
            largest_party_percent = 0
            for party in cluster_counts[cluster]:
                party_percent = cluster_counts[cluster][party]/total_members
                if party_percent > largest_party_percent:
                    largest_party_percent = party_percent
            party_percents.append(largest_party_percent)
        return sum(1/len(cluster_counts) * i for i in party_percents)

    def __init__(self, data_dir, metadata_files, chamber, verbose_output):
        super(ClusterCongress, self).__init__()
        dataman = DataManager()
        record, ids = dataman.parse_votes(data_dir, chamber)
        self.voting_record = VoteRecord(record, ids)
        self.members = dataman.parse_members(metadata_files)
        self.verbose = verbose_output

def cluster_all_congresses(root_dir, chamber_name, verbose, outfile, k=2):
    """ cluster all congresses by voting record and determine how partisan each one was """

    if str.lower(chamber_name) == 'house':
        chamber = Chamber.house
    elif str.lower(chamber_name) == 'senate':
        chamber = Chamber.senate
    else:
        print('ERROR: {0} is not a valid chamber name. Use either "house" or "senate"'.format(chamber_name))

    # directory structure like Data/congress number/votes/year/bill number/data.xml
    # handle only wanting to cluster 1 congress
    if 'votes' in os.listdir(root_dir):
        c = ClusterCongress(root_dir, 
                            ['Data/legislators-current.csv', 'Data/legislators-historic.csv'], 
                            chamber, verbose)
        c.cluster(k)
        partisanship = c.check_party_affiliation()
        print(partisanship)
        return partisanship
    else:
        congress_dirs = sorted([int(i) for i in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, i))])
        partisanships = []
        for directory in congress_dirs:
            sys.stdout.write('\rClustering Congress {0}'.format(directory))
            c = ClusterCongress(root_dir+'/'+str(directory), 
                                ['Data/legislators-current.csv', 'Data/legislators-historic.csv'], 
                                chamber, verbose)
            c.cluster(k)
            partisanships.append((directory, c.check_party_affiliation()))
        with open(outfile, 'w') as f:
            writer = csv.writer(f, delimiter=',')
            for p in partisanships:
                writer.writerow(p)
        return partisanships

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--chamber', required = True, help = 'Chamber of Congress, either "house" or "senate"')
    parser.add_argument('-d', '--datadir', required = True, help = 'Data directory with voting records')
    parser.add_argument('-o', '--outputfile', required = True, help = 'File in which to save results')
    parser.add_argument('-v', '--verbose', required = False, action = 'store_true')
    parser.add_argument('-k', '--num_clusters', required = True, help = 'number of clusters into which to place congress')
    args = parser.parse_args()

    cluster_all_congresses(args.datadir, args.chamber, args.verbose, args.outputfile, int(args.num_clusters))

    # c = ClusterCongress('Data', ['Data/legislators-current.csv', 'Data/legislators-historic.csv'], Chamber.senate)
    # c.cluster(2)
    # c.check_party_affiliation()

if __name__ == '__main__':
    main()