import os
from setuptools import setup, find_packages

setup(
    name="PyStreamMCP",
    version="0.3.0",
    description="Intelligence layer for AI agents - query planning, discovery, cost optimization",
    author="Georgi Mammen Mullassery",
    author_email="mullassery@gmail.com",
    license="MIT",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    install_requires=["pydantic>=2.0"],
    python_requires=">=3.9",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Mullassery/PyStreamMCP",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
