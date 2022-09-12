import json
from pkg_resources import resource_filename

data_file = resource_filename("resotodata", "data/regions.json")
with open(data_file) as f:
    regions = json.load(f)
