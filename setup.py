from setuptools import find_packages, setup

setup(
    name="ganreport",
    version="3.0.0",
    author="Wugapodes",
    author_email="wugapodes@gmail.com",
    description="Produces a report on English Wikipedia's Good Article project backlog.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Wugapodes/GANReport",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "ganreport=ganreport.main:main",  # Command line entry
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
