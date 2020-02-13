# -*- coding: utf-8 -*-
"""

"""

import sys
from os.path import join, dirname
from setuptools import setup
import tranny

requirements = [l.strip() for l in open("requirements.txt").readlines()]

if sys.version_info < (2, 7):
    requirements.append("argparse")

setup(
    name="tranny",
    version=tranny.__version__,
    url="https://github.com/leighmacdonald/tranny/",
    license="BSD-3",
    description="Torrent management systems",
    author="Leigh MacDonald",
    author_email="leigh.macdonald@gmail.com",
    long_description=open(join(dirname(__file__), "README.md")).read(),
    scripts=['tranny-cli.py'],
    packages=[
        "tranny",
        "tranny.client",
        "tranny.handlers",
        "tranny.notification",
        "tranny.provider",
        "tranny.service"
    ],
    package_data={'tranny': ['tranny/templates']},
    install_requires=requirements,
    test_suite="tests",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: BSD License"
    ]
)
