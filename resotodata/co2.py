import json
from pkg_resources import resource_filename

data_file = resource_filename("resotodata", "data/ccfdataset.json")
with open(data_file) as f:
    ccfdataset = json.load(f)
