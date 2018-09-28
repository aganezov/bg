__author__ = 'aganezov'

from setuptools import setup

from bg import version as bg_version

setup(
    name="bg",
    version=bg_version,
    packages=["bg", "tests"],
    install_requires=['coverage', 'decorator', 'networkx>=2', 'nose', 'marshmallow', 'ete3',
                      'six', 'mock', 'pytest', 'scipy', 'numpy', 'enum-compat'],
    author="Sergey Aganezov",
    author_email="aganezov@cs.jhu.edu",
    description="Implementation of Breakpoint Graph data structure",
    license="MIT",
    keywords=["breakpoint graph", "data structures", "python"],
    url="https://github.com/aganezov/bg",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
