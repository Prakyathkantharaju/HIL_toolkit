from setuptools import setup, find_packages

setup(
    name="HIL",
    version="0.0.1",
    packages=find_packages(include=["HIL", "HIL.optimization.*"])
)