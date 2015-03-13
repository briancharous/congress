from collections import namedtuple
from enum import Enum
import json
import os
import xml.etree.ElementTree as ET


class Chamber(Enum):
    house = 1
    senate = 2


class DataManager(object):

    def voting_record(self, dir, chamber):
        paths = self._collect_data_paths(dir, chamber)
        vote_record = {}
        Vote = namedtuple('Vote', ['yays', 'nays', 'not_voting', 'present'])
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
                        voter_id = child.attrib['id']
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
        return vote_record

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

    def __init__(self,):
        super(DataManager, self).__init__()


def main():
    d = DataManager()
    print(d.voting_record('.', Chamber.house))

if __name__ == '__main__':
    main()
