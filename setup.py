from setuptools import find_packages, setup

setup(
    name="src",
    packages=find_packages(),
    version="0.0.1",
    description="Housing Scraping NL",
    author="Michele Tonutti",
    license="",
    install_requires=[
        "beautifulsoup4~=4.10.0",
        "fake-useragent~=0.1.11",
        "requests~=2.26.0",
        "tqdm~=4.62.3",
    ],
    extras_require={
        "cicd": ["black=21.11b1", "coverage==6.1.2"],
    },
)
