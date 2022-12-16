from setuptools import setup, find_packages

setup(
    author = "Petros Tepoyan",
    description = "A package for RFMAnalaysis",
    name = "RFMAnalysis",
    version = "0.1.0",
    packages = find_packages(include = [
        "pandas", 
        "numpy",
        "squarify", 
        "seaborn", 
        "matplotlib"]),
    install_requires = [
        "pandas", 
        "numpy",
        "squarify", 
        "seaborn", 
        "matplotlib"]
)