import fixinventorydata
from setuptools import setup, find_packages


with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("requirements-dev.txt") as f:
    dev_required = f.read().splitlines()

with open("requirements-test.txt") as f:
    test_required = f.read().splitlines()

with open("README.md") as f:
    readme = f.read()


setup(
    name=fixinventorydata.__title__,
    version=fixinventorydata.__version__,
    description=fixinventorydata.__description__,
    license=fixinventorydata.__license__,
    packages=find_packages(),
    long_description=readme,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "fixinventorydata-update-regions = fixinventorydata.__main__:update_regions",
            "fixinventorydata-update-colors = fixinventorydata.__main__:update_colors",
            "fixinventorydata-update-ccfdataset = fixinventorydata.__main__:update_ccfdataset",
            "fixinventorydata-update-instances = fixinventorydata.__main__:update_instances",
        ]
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    extras_require={"dev": dev_required},
    setup_requires=["pytest-runner"],
    tests_require=test_required,
    classifiers=[
        # Current project status
        "Development Status :: 4 - Beta",
        # Audience
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        # License information
        "License :: OSI Approved :: Apache Software License",
        # Supported python versions
        "Programming Language :: Python :: 3.9",
        # Supported OS's
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        # Extra metadata
        "Environment :: Console",
        "Natural Language :: English",
        "Topic :: Security",
        "Topic :: Utilities",
    ],
    keywords="cloud security",
)
