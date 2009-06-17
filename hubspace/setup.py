from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='hubspace',
      version=version,
      description="hub space management",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='hub space management',
      author='tom salfield',
      author_email='tom.salfield@the-hub.net',
      url='the-hub.net',
      license='GPLV2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
