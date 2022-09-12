import json
import requests
from pkg_resources import resource_filename
from geopy.geocoders import Nominatim
from geopy.location import Location
from typing import Optional
from bs4 import BeautifulSoup


def main() -> None:
    pass


def update_regions() -> None:
    regions = {}
    regions["gcp"] = gen_gcp_regions()
    regions["aws"] = gen_aws_regions()
    write_regions(regions)


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
        location = lookup_location(location)
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
        location = lookup_location(location)
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
        return geolocator.geocode(long_region)
    except Exception:
        return None


if __name__ == "__main__":
    main()
