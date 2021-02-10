from setuptools import setup, find_packages

setup(
    name='webcheck',
    version='1.0.0',
    url='https://github.com/throwaway-ps/aiven-test',
    author='Patrick Stählin',
    author_email='me@packi.ch',
    description='Checks uris and records their state',
    packages=find_packages(),
    install_requires=['psycopg2 >= 2.6.8', 'requests >= 2.22.0', 'kafka-python >= 2.0.2'],
)
