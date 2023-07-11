import os
import json
import shutil
import requests
import tempfile
import subprocess
from pkg_resources import resource_filename
from geopy.geocoders import Nominatim
from geopy.location import Location
from typing import Optional
from bs4 import BeautifulSoup


def main() -> None:
    pass


def update_regions() -> None:
    regions = {}
    regions["aws"] = gen_aws_regions()
    regions["digitalocean"] = gen_digitalocean_regions()
    regions["gcp"] = gen_gcp_regions()
    write_regions(regions)


def update_colors() -> None:
    write_colors()


def update_ccfdataset() -> None:
    write_ccfdataset()


def gen_digitalocean_regions() -> dict:
    print("Processing DigitalOcean regions")
    regions = {}
    DIGITALOCEAN_TOKEN = os.environ.get("DIGITALOCEAN_TOKEN")
    regions_url = "https://api.digitalocean.com/v2/regions"
    if DIGITALOCEAN_TOKEN is None:
        regions_in = {
            "nyc1": "New York 1",
            "sfo1": "San Francisco 1",
            "nyc2": "New York 2",
            "ams2": "Amsterdam 2",
            "sgp1": "Singapore 1",
            "lon1": "London 1",
            "nyc3": "New York 3",
            "ams3": "Amsterdam 3",
            "fra1": "Frankfurt 1",
            "tor1": "Toronto 1",
            "sfo2": "San Francisco 2",
            "blr1": "Bangalore 1",
            "sfo3": "San Francisco 3",
            "syd1": "Sydney 1",
        }
    else:
        headers = {"Authorization": f"Bearer {DIGITALOCEAN_TOKEN}"}
        r = requests.get(regions_url, headers=headers)
        regions_in = {reg["slug"]: reg["name"] for reg in r.json()["regions"]}
    for short_region, long_region in regions_in.items():
        location = lookup_location(short_region, long_region.rsplit(" ", 1)[0])
        regions[short_region] = {
            "short_name": short_region,
            "long_name": long_region,
            "latitude": location.latitude,
            "longitude": location.longitude,
        }
    return regions


def gen_gcp_regions() -> dict:
    print("Processing GCP regions")
    regions = {}
    locations_url = "https://cloud.google.com/about/locations"
    r = requests.get(locations_url)
    soup = BeautifulSoup(r.text, "html.parser")
    for loc in soup.find_all("span", {"class": "zone"}):
        long_region = loc.previous_sibling
        short_region = loc.text
        if "(" in short_region and ")" in short_region:
            short_region = short_region[short_region.find("(") + 1 : short_region.find(")")]
        location = extract_gcp_location(short_region, long_region)
        location = lookup_location(short_region, location)
        regions[short_region] = {
            "short_name": short_region,
            "long_name": long_region,
            "latitude": location.latitude,
            "longitude": location.longitude,
        }
    return regions


def gen_aws_regions() -> dict:
    print("Processing AWS regions")
    regions = {}
    for short_region, long_region in aws_regions().items():
        location = extract_aws_location(short_region, long_region)
        location = lookup_location(short_region, location)
        if location is None:
            print(f"Failed to lookup {short_region} {long_region}")
            continue

        regions[short_region] = {
            "short_name": short_region,
            "long_name": long_region,
            "latitude": location.latitude,
            "longitude": location.longitude,
        }
    return regions


def write_regions(regions: dict) -> None:
    regions_file = resource_filename("resotodata", "data/regions.json")
    print(f"Writing regions to {regions_file}")
    with open(regions_file, "w") as f:
        json.dump(regions, f, indent=4)
        f.write("\n")


aws_override = {
    "ca-central-1": "Montréal, Québec, Canada",
    "eu-west-1": "Dublin, Ireland",
    "me-central-1": "Dubai, United Arab Emirates",
    "us-east-1": "Ashburn, Virginia, USA",
    "us-east-2": "Columbus, Ohio, USA",
    "us-west-1": "San Francisco, California, USA",
    "us-west-2": "Boardman, Oregon, USA",
}

gcp_override = {
    "us-west1": "The Dalles, Oregon, USA",
    "us-west2": "Los Angeles, California, USA",
    "us-west3": "Salt Lake City, Utah, USA",
    "us-west4": "Las Vegas, Nevada, USA",
    "us-east1": "Moncks Corner, South Carolina, USA",
    "us-east4": "Ashburn, Virginia, USA",
    "us-central1": "Council Bluffs, Iowa, USA",
    "us-south1": "Dallas, Texas, USA",
    "europe-west1": "St. Ghislain, Belgium",
    "europe-west4": "Eemshaven, Netherlands",
    "europe-north1": "Hamina, Finland",
    "southamerica-west1": "Santiago, Chile",
}


def extract_aws_location(short_region: str, long_region: str) -> str:
    if short_region in aws_override:
        return aws_override[short_region]
    if "(" in long_region and ")" in long_region:
        return long_region[long_region.find("(") + 1 : long_region.find(")")]
    return long_region


def extract_gcp_location(short_region: str, long_region: str) -> str:
    if short_region in gcp_override:
        return gcp_override[short_region]
    if "(" in long_region and ")" in long_region:
        return long_region[long_region.find("(") + 1 : long_region.find(")")]
    return long_region


def aws_regions() -> dict:
    endpoint_file = resource_filename("botocore", "data/endpoints.json")
    with open(endpoint_file, "r") as f:
        endpoints = json.load(f)
        first_partition = next(iter(endpoints.get("partitions", [])), {})
        regions = {k: v["description"] for k, v in first_partition.get("regions", {}).items()}
        return regions


def lookup_location(short_region: str, long_region: str) -> Optional[Location]:
    try:
        print(f"Looking up {short_region} {long_region}")
        geolocator = Nominatim(user_agent="ResotoMisc")
        loc = geolocator.geocode(long_region)
        print(f"Found {loc}")
        return loc
    except Exception:
        return None


def write_colors() -> None:
    colors = {
        "resoto": {
            "light": {
                "main": [0x762DD7, 0x0A253F, 0xAF62F1],
                "contrast": [0xFFAF37, 0xE59010, 0xB86200],
                "background": [0xFFFFFF, 0xEBF2FC, 0x3D176E, 0x0F3356],
            },
            "dark": {
                "main": [0xD9B8FF, 0xE98DF7, 0xC38FFF, 0xFFFFFF],
                "contrast": [0xFFE797, 0x762DD7, 0xFFAF37, 0xE59010],
                "background": [0x0F3356, 0x0A253F, 0x3D176E, 0x000D19],
            },
        },
        "someengineering": {
            "light": {
                "main": [0x0F3356, 0x0054A3, 0x1A83AF],
                "contrast": [0xFFAF37, 0xE59010, 0xB86200],
                "background": [0xFFFFFF, 0xEBF2FC, 0x0F3356],
            },
            "dark": {
                "main": [0x89D1F1, 0x1A83AF, 0x0054A3, 0xFFFFFF],
                "contrast": [0xFFE797, 0xFFAF37, 0xDDA045],
                "background": [0x0F3356, 0x0A253F, 0x000D19],
            },
        },
    }

    colors_file = resource_filename("resotodata", "data/colors.json")
    print(f"Writing colors to {colors_file}")
    with open(colors_file, "w") as f:
        json.dump(colors, f, indent=4)
        f.write("\n")


def write_ccfdataset() -> None:
    ccfdataset = get_ccfdataset()

    ccfdataset_file = resource_filename("resotodata", "data/ccfdataset.json")
    print(f"Writing CCF dataset to {ccfdataset_file}")
    with open(ccfdataset_file, "w") as f:
        json.dump(ccfdataset, f, indent=4)
        f.write("\n")


def get_ccfdataset() -> dict:
    print("Checking if git and npm are installed")
    for tool in ("git", "npm"):
        if not shutil.which(tool):
            raise RuntimeError(f"{tool} not found in path")

    ccfrepo = "https://github.com/cloud-carbon-footprint/cloud-carbon-footprint.git"

    export_ts = """import {
  AWS_CLOUD_CONSTANTS,
  AWS_EMISSIONS_FACTORS_METRIC_TON_PER_KWH,
} from './packages/aws/src/domain/AwsFootprintEstimationConstants'
import { GCP_CLOUD_CONSTANTS, getGCPEmissionsFactors } from './packages/gcp/src/domain/GcpFootprintEstimationConstants'
import {
  AZURE_CLOUD_CONSTANTS,
  AZURE_EMISSIONS_FACTORS_METRIC_TON_PER_KWH,
} from './packages/azure/src/domain/AzureFootprintEstimationConstants'
import { configLoader } from '@cloud-carbon-footprint/common'

const combinedDictionary: { [key: string]: any } = {
  aws: {
    AWS_CLOUD_CONSTANTS: AWS_CLOUD_CONSTANTS,
    AWS_EMISSIONS_FACTORS_METRIC_TON_PER_KWH: AWS_EMISSIONS_FACTORS_METRIC_TON_PER_KWH,
  },
  gcp: {
    GCP_CLOUD_CONSTANTS: GCP_CLOUD_CONSTANTS,
    GCP_EMISSIONS_FACTORS_METRIC_TON_PER_KWH: getGCPEmissionsFactors(),
  },
  azure: {
    AZURE_CLOUD_CONSTANTS: AZURE_CLOUD_CONSTANTS,
    AZURE_EMISSIONS_FACTORS_METRIC_TON_PER_KWH: AZURE_EMISSIONS_FACTORS_METRIC_TON_PER_KWH,
  },
}
configLoader().GCP.USE_CARBON_FREE_ENERGY_PERCENTAGE = true
combinedDictionary['gcp']['GCP_EMISSIONS_FACTORS_METRIC_TON_PER_KWH_CFE'] = getGCPEmissionsFactors()

console.log(JSON.stringify(combinedDictionary, null, 2))
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Cloning {ccfrepo} to {tmpdir}")
        subprocess.run(["git", "clone", ccfrepo, tmpdir], check=True)
        print(f"Installing dependencies in {tmpdir}")
        subprocess.run(["npm", "install", "--legacy-peer-deps", "--silent"], cwd=tmpdir, check=True)
        print("Installing ts-node")
        subprocess.run(["npm", "install", "--silent", "ts-node"], cwd=tmpdir, check=True)

        export_file = os.path.join(tmpdir, "export.ts")
        with open(export_file, "w") as f:
            f.write(export_ts)

        print("Exporting CCF dataset constants")
        result = subprocess.run(
            ["./node_modules/.bin/ts-node", "export.ts"], cwd=tmpdir, check=True, capture_output=True, text=True
        )

    return json.loads(result.stdout)


if __name__ == "__main__":
    main()
