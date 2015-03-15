import os
import sys
from subprocess import call
from urllib import request

call(['mkdir', '-p', 'Data'])
os.chdir('Data')
call(['rsync', '-avz', '--delete', '--delete-excluded', '--exclude-from', '../exclude.txt', 
     'govtrack.us::govtrackdata/congress/', '.'])
request.urlretrieve('https://www.govtrack.us/data/congress-legislators/legislators-historic.csv', 'legislators-historic.csv')
request.urlretrieve('https://www.govtrack.us/data/congress-legislators/legislators-current.csv', 'legislators-current.csv')