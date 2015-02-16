__author__ = 'aganezov'

from setuptools import setup

from bg import version as bg_version
setup(
    name="bg",
    version=bg_version,
    packages=["bg"],
    install_requires=list(map(lambda entry: entry.strip(), open("requirements.txt", "rt").readlines())),
    author="Sergey Aganezov",
    author_email="aganezov@gwu.edu",
    description="Implementation of Breakpoint Graph data structure",
    license="GPLv3",
    keywords=["breakpoint graph", "data structures", "python"],
    url="https://github.com/sergey-aganezov-jr/bg"
)