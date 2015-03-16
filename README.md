This program clusters members of Congress and tries to quantify how bipartisan a given session of Congress is based on its voting record.

#Setup
-----------------
This program requires `Python 3.4` and the following librarires: `numpy 1.9.x`, `scipy 0.15.x`, and `scikit-learn 0.15.x`. The requirements are listed in `requirements.txt` and can be installed with

`pip3 install -r requirements.txt`


The dataset required for this program to run is available from [govtrack](govtrack.us). To get the data `rsync` is required. From the project directory, run

`python3 fetchdata.py`

This may take awhile since there is a little over 1GB of data files, but when finished, it should create a directory called `Data` in the project directory. 

#Run
----------------
To run the clustering, run `clustercongress.py` with `python3`. This program takes several flags. 

`-c` followed by either `house` or `senate`

`-d` is the top level directory in which the data files are stored. Running with the `Data/` directory will cluster every single Congress, while running with `Data/###` where `###	` is the Congress number will run on only one session of Congress

`-o` is the output file in which to save a CSV of the partisanship rating

`-v` is an optional flag. If provided, the program will print out the members of each cluster

`-k` is the number of clusters to search for