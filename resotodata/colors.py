import json
from pkg_resources import resource_filename

data_file = resource_filename("resotodata", "data/colors.json")
with open(data_file) as f:
    colors = json.load(f)
