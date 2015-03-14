from collections import namedtuple
import csv
from enum import Enum
import json
import numpy as np
import os
import time
import xml.etree.ElementTree as ET


class Chamber(Enum):
    house = 1
    senate = 2

class VoteRecord(object):
    """ abstraction of voting record backed up by numpy matrix """

    def _init_structure(self):
        """ initialize the matrix data sturcture """
        # matrix like
        #            | bill_id 1 yay | bill_id 1 nay | bill_id 1 not voting | bill_id 1 present | ...
        # voter_id 1 |       1       |       0       |          0           |         0         |
        # voter_id 2 |       0               1       |          0           |         0         |
        # .......... | 
        
        # create dictionary to map voter id to row in the matrix
        # {voter_id: row #} and vicd versa
        for i in range(len(self.voter_ids_list)):
            self.voter_row_mappings[self.voter_ids_list[i]] = i
            self.row_voter_mappings[i] = self.voter_ids_list[i]

        # dictionary to map bill id to (start) column in the matrix
        # {bill_id: start column #}
        bill_ids = list(self.record.keys())
        for i in range(len(bill_ids)):
            self.bill_col_mappings[bill_ids[i]] = i*4

        self.matrix = np.zeros((len(self.voter_ids), 4*len(self.record)))
        for bill_id in self.record:
            vote = self.record[bill_id]
            yays = vote.yays
            nays = vote.nays
            not_voting = vote.not_voting
            present = vote.present
            for vid in yays:
                row = self.voter_row_mappings[vid]
                column = self.bill_col_mappings[bill_id]
                self.matrix[row][column] = 1
            for vid in nays:
                row = self.voter_row_mappings[vid]
                column = self.bill_col_mappings[bill_id]+1
                self.matrix[row][column] = 1
            for vid in not_voting:
                row = self.voter_row_mappings[vid]
                column = self.bill_col_mappings[bill_id]+2
                self.matrix[row][column] = 1
            for vid in present:
                row = self.voter_row_mappings[vid]
                column = self.bill_col_mappings[bill_id]+3
                self.matrix[row][column] = 1

    def __init__(self, record, voter_ids):
        super(VoteRecord, self).__init__()
        self.record = record
        self.voter_ids = voter_ids
        self.voter_ids_list = list(self.voter_ids)
        self.matrix = None    
        self.voter_row_mappings = {}
        self.row_voter_mappings = {}
        self.bill_col_mappings = {}

        self._init_structure()


class DataManager(object):

    def parse_votes(self, dir, chamber):
        """ read vote record from all data files in a given directory for house or senate """
        paths = self._collect_data_paths(dir, chamber)
        vote_record = {}
        Vote = namedtuple('Vote', ['yays', 'nays', 'not_voting', 'present'])
        voters = set()
        for path in paths:
            with open(os.path.abspath(path), 'r') as f:
                root = ET.fromstring(f.read())
                yays = []
                nays = []
                not_voting = []
                present = []
                vote_id = self._vote_id(root.attrib)
                for child in root:
                    if child.tag == "voter":
                        voter_id = int(child.attrib['id'])
                        voters.add(voter_id)
                        vote = child.attrib['vote']
                        if vote == '+':
                            yays.append(voter_id)
                        elif vote == '-':
                            nays.append(voter_id)
                        elif vote == 'P':
                            present.append(voter_id)
                        elif vote == '0':
                            not_voting.append(voter_id)
                vote = Vote(yays = yays,
                            nays = nays,
                            not_voting = not_voting,
                            present = present)
                vote_record[vote_id] = vote
        return vote_record, voters

    def parse_members(self, filenames):
        """ read metadata for members of congress """
        Member = namedtuple('Member', ['first_name', 
                                       'last_name', 
                                       'party',
                                       'id',
                                       'state',
                                       'district',
                                       'gender',
                                       'birthday'])
        members = {}
        for filename in filenames:
            with open(filename, 'r') as f:
                next(f)
                reader = csv.reader(f, delimiter=',')
                for row in reader:
                    if row[2] != '':
                        birthday = time.strptime(row[2], '%Y-%m-%d')
                    else:
                        birthday = None
                    district = row[6]
                    if district != '':
                        district = int(district)
                    else:
                        district = None
                    voter_id = int(row[23])
                    member = Member(first_name = row[1],
                                    last_name = row[0],
                                    party = row[7],
                                    id = voter_id,
                                    state = row[5],
                                    district = district,
                                    gender = row[3],
                                    birthday = birthday)
                    members[voter_id] = member
        return members

    def _vote_id(self, attributes):
        prefix = ''
        if attributes['where'] == 'house': 
            prefix = 'h'
        elif attributes['where'] == 'senate':
            prefix = 's'
        assert prefix is not ''
        session = attributes['session']
        roll = attributes['roll']
        return '{0}-{1}.{2}'.format(prefix, session, roll)

    def _collect_data_paths(self, base_path, chamber):
        """ traverse directory tree and get all JSON file paths
        for house or senate """
        file_paths = []
        for path, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.xml'):
                    # directory sturcture like /votes/2015/h1/data.xml
                    # where h1 represents the 1st vote made by the house
                    # and something like s1 is the 1st vote in the senate
                    chamber_id = os.path.split(path)[1][0]
                    if chamber == Chamber.house and chamber_id == 'h':
                        file_paths.append(
                            os.path.join(os.path.abspath(path), file))
                    elif chamber == Chamber.senate and chamber_id == 's':
                        file_paths.append(
                            os.path.join(os.path.abspath(path), file))
        return file_paths

    def __init__(self):
        super(DataManager, self).__init__()


def main():
    d = DataManager()
    votes, ids = d.parse_votes('.', Chamber.house)
    r = VoteRecord(votes, ids)
    d.parse_members('Data/legislators-current.csv')

if __name__ == '__main__':
    main()
