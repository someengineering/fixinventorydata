import json
from pkg_resources import resource_filename
from geopy.geocoders import Nominatim
from geopy.location import Location
from typing import Optional


def main() -> None:
    pass


def update_regions() -> None:
    regions = {}
    regions["aws"] = gen_aws_regions()
    write_regions(regions)


def gen_aws_regions() -> dict:
    print("Looking up AWS regions")
    regions = {}
    for short_region, long_region in aws_regions().items():
        location = extract_aws_location(short_region, long_region)
        print(f"{short_region} {location}")
        location = lookup_location(location)
        if location is None:
            print(f"Failed to lookup {location}")
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


def extract_aws_location(short_region: str, long_region: str) -> str:
    if short_region in aws_override:
        return aws_override[short_region]
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


def lookup_location(location: str) -> Optional[Location]:
    try:
        geolocator = Nominatim(user_agent="ResotoMisc")
        return geolocator.geocode(location)
    except Exception:
        return None


if __name__ == "__main__":
    main()
