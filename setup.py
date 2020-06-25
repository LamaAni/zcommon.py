#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def get_version():
    version_file_path = os.path.join(here, "package_version.txt")
    if not os.path.isfile(version_file_path):
        return "debug"
    version = None
    with open(version_file_path, "r") as raw:
        version = raw.read()

    return version


setup(
    name="zcommon",
    version=get_version(),
    description="A collection of common methods and utils.",
    long_description="Please see the github repo and help @ https://github.com/LamaAni/zcommon.py",
    classifiers=[],
    author="Zav Shotan",
    author_email="",
    url="https://github.com/LamaAni/zcommon.py",
    packages=["zcommon"],
    platforms="any",
    license="LICENSE",
    install_requires=["match_pattern"],
    python_requires=">=3.6",
    include_package_data=True,
)
