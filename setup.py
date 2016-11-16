__author__ = 'aganezov'
import os
from setuptools import setup

from bg import version as bg_version
setup(
    name="bg",
    version=bg_version,
    packages=["bg", "tests"],
    install_requires=list(map(lambda entry: entry.strip(), open(os.path.join(os.path.dirname(__file__), "requirements.txt"), "rt").readlines())),
    author="Sergey Aganezov",
    author_email="aganezov@gwu.edu",
    description="Implementation of Breakpoint Graph data structure",
    license="LGPLv3",
    keywords=["breakpoint graph", "data structures", "python"],
    url="https://github.com/aganezov/bg",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)