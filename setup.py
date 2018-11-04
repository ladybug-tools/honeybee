import re
import setuptools
import sys

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('honeybee/__init__.py', 'r') as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(),
        re.MULTILINE
    ).group(1)

try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    pass

setuptools.setup(
    name="lbt-honeybee",
    version=version,
    author="Ladybug Tools",
    author_email="info@ladybug.tools",
    description="Honeybee is a Python library to create, run and visualize the results of daylight (RADIANCE) and energy analysis (EnergyPlus/OpenStudio). The current version supports only Radiance integration.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ladybug-tools/honeybee",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'lbt-ladybug'
    ],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ],
)
