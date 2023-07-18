import resotodata
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
    name=resotodata.__title__,
    version=resotodata.__version__,
    description=resotodata.__description__,
    license=resotodata.__license__,
    packages=find_packages(),
    long_description=readme,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "resotodata-update-regions = resotodata.__main__:update_regions",
            "resotodata-update-colors = resotodata.__main__:update_colors",
            "resotodata-update-ccfdataset = resotodata.__main__:update_ccfdataset",
            "resotodata-update-instances = resotodata.__main__:update_instances",
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
