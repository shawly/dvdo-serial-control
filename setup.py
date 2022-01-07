# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="dvdosc",
    version="0.1.0",
    description="Application to control DVDO iScan video processors through an RS232 serial connection.",
    long_description=readme,
    author="shawly",
    author_email="shawlyde@gmail.com",
    url="https://github.com/shawly/dvdo-serial-control",
    license=license,
    packages=find_packages(exclude=("tests")),
)
