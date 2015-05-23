#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = "0.1.1"


setup(
    name="redcrab",
    author="Gregory Rehm",
    version=__version__,
    description="A crawler for the Reddit API that will take comments and store them in a database",
    packages=find_packages(),
    package_data={"*": ["*.html"]},
    install_requires=[
        "praw",
        "psycopg2",
    ],
    entry_points={
        "console_scripts": [
            "redcrab=redcrab.main:main",
        ]
    }
)
