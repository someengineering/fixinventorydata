import os
import venv
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
    ccfdataset = get_ccfdataset()
    write_ccfdataset(ccfdataset)


def update_instances() -> None:
    instances = {"aws": get_aws_instances()}
    strip_instances(instances)
    write_instances(instances)


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
    regions_file = resource_filename("fixinventorydata", "data/regions.json")
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
        geolocator = Nominatim(user_agent="FixInventoryMisc")
        loc = geolocator.geocode(long_region)
        print(f"Found {loc}")
        return loc
    except Exception:
        return None


def write_colors() -> None:
    colors = {
        "fixinventory": {
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

    colors_file = resource_filename("fixinventorydata", "data/colors.json")
    print(f"Writing colors to {colors_file}")
    with open(colors_file, "w") as f:
        json.dump(colors, f, indent=4)
        f.write("\n")


def write_ccfdataset(ccfdataset: dict) -> None:
    ccfdataset_file = resource_filename("fixinventorydata", "data/ccfdataset.json")
    print(f"Writing CCF dataset to {ccfdataset_file}")
    with open(ccfdataset_file, "w") as f:
        json.dump(ccfdataset, f, indent=4)
        f.write("\n")


def write_instances(instances: dict) -> None:
    instances_file = resource_filename("fixinventorydata", "data/instances.json")
    print(f"Writing instances dataset to {instances_file}")
    with open(instances_file, "w") as f:
        json.dump(instances, f, indent=4)
        f.write("\n")


def is_float(n) -> bool:
    try:
        _ = float(n)
    except ValueError:
        return False
    else:
        return True


def strip_instances(instances: dict) -> None:
    print("Stripping instance data")
    spot_keywords = ["spot", "spot_min", "spot_max"]
    for cloud, cloud_data in instances.items():
        for instance_type, instance_type_data in cloud_data.items():
            for region, region_pricing_data in instance_type_data.get("pricing", {}).items():
                for key in list(region_pricing_data.keys()):
                    if key not in ("dedicated", "linux", "unknown"):
                        del region_pricing_data[key]
                if "linux" in region_pricing_data:
                    for keyword in spot_keywords:
                        try:
                            del region_pricing_data["linux"][keyword]
                        except KeyError:
                            pass
                for price_data in region_pricing_data.values():
                    if "ondemand" in price_data and is_float(price_data["ondemand"]):
                        price_data["ondemand"] = float(price_data["ondemand"])
                    if "reserved" in price_data and isinstance(price_data["reserved"], dict):
                        for terms, price in price_data["reserved"].items():
                            if is_float(price):
                                price_data["reserved"][terms] = float(price)


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

    ccfdataset = json.loads(result.stdout)

    # Add missing AMD EPYC 3rd Gen data to AWS
    aws_cloud_constants = ccfdataset.get("aws", {}).get("AWS_CLOUD_CONSTANTS", {})
    azure_cloud_constants = ccfdataset.get("azure", {}).get("AZURE_CLOUD_CONSTANTS", {})
    if (
        not "AMD EPYC 3rd Gen" in aws_cloud_constants["MIN_WATTS_BY_COMPUTE_PROCESSOR"]
        and "AMD EPYC 3rd Gen" in azure_cloud_constants["MIN_WATTS_BY_COMPUTE_PROCESSOR"]
    ):
        aws_cloud_constants["MIN_WATTS_BY_COMPUTE_PROCESSOR"]["AMD EPYC 3rd Gen"] = azure_cloud_constants[
            "MIN_WATTS_BY_COMPUTE_PROCESSOR"
        ]["AMD EPYC 3rd Gen"]
        aws_cloud_constants["MAX_WATTS_BY_COMPUTE_PROCESSOR"]["AMD EPYC 3rd Gen"] = azure_cloud_constants[
            "MAX_WATTS_BY_COMPUTE_PROCESSOR"
        ]["AMD EPYC 3rd Gen"]
        aws_cloud_constants["MEMORY_BY_COMPUTE_PROCESSOR"]["AMD EPYC 3rd Gen"] = azure_cloud_constants[
            "MEMORY_BY_COMPUTE_PROCESSOR"
        ]["AMD EPYC 3rd Gen"]

    return ccfdataset


def get_aws_instances() -> dict:
    print("Checking if git is installed")
    for tool in ("git",):
        if not shutil.which(tool):
            raise RuntimeError(f"{tool} not found in path")

    ec2instancesrepo = "https://github.com/vantage-sh/ec2instances.info.git"

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Cloning {ec2instancesrepo} to {tmpdir}")
        subprocess.run(["git", "clone", ec2instancesrepo, tmpdir], check=True)

        # Create venv
        venv_dir = os.path.join(tmpdir, "venv")
        venv.create(venv_dir, with_pip=True)

        # Paths to python and pip executables in venv
        venv_python = os.path.join(venv_dir, "bin", "python")
        venv_pip = os.path.join(venv_dir, "bin", "pip")

        print(f"Installing dependencies in {tmpdir}")
        subprocess.run([venv_pip, "install", "-r", "requirements.txt"], cwd=tmpdir, check=True)
        print("Invoking build")
        subprocess.run([venv_python, "-m", "invoke", "-T", "3600", "build"], cwd=tmpdir, check=True)

        instances_file = os.path.join(tmpdir, "www", "instances.json")
        with open(instances_file) as f:
            instance_types = json.load(f)

        instances = {}
        for instance_type in instance_types:
            instance_type_name = instance_type.get("instance_type")
            if instance_type_name is None:
                print(f"Skipping invalid instance type: {instance_type}")
                continue
            instances[instance_type_name] = instance_type

        return instances


if __name__ == "__main__":
    main()
