from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in salesforce_management/__init__.py
from salesforce_management import __version__ as version

setup(
	name="salesforce_management",
	version=version,
	description="Salesforce Management",
	author="BluePhoenix",
	author_email="bluephoenix00995@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
