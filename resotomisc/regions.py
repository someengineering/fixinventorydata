import json
from pkg_resources import resource_filename

regions_file = resource_filename("resotomisc", "gen/regions.json")
with open(regions_file) as f:
    cloud_regions = json.load(f)
