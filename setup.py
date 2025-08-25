from setuptools import find_packages, setup
import subprocess
import pkg_resources
import sys

setup(
    name="WTelethon",
    packages=find_packages(exclude=["tests"]),
    version="0.1.0",
    description="Wrapper for Telethon",
    author="anon",
    license="MIT",
    install_requires=[
        "phonenumbers",
        "pytz",
        "pydantic",
        "python_socks[asyncio]",
        "loguru",

    ],
)
