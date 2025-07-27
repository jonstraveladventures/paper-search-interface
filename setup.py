#!/usr/bin/env python3
"""
Setup script for Paper Search Interface
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="paper-search-interface",
    version="1.0.0",
    author="Jonathan Shock",
    author_email="jonathan.shock@uct.ac.za",
    description="A comprehensive web interface for searching through 200,000+ academic papers from major AI/ML conferences",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jonstraveladventures/paper-search-interface",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "paper-search=tools.web_interface:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.csv", "*.txt", "templates/*.html"],
    },
) 