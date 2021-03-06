from setuptools import setup, find_packages
#from turbogears.finddata import find_package_data
import sys, os

version = '1.0'

setup(name='hubspace',
      version=version,
      description="Hub space management system",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='hub space mangement',
      author='tom salfield',
      author_email='tom.salfield@the-hub.net',
      url='the-hub.net',
      license='GPL',
      packages=find_packages(),
      #package_data = find_package_data(where='hubspace',
      #                                 package='hubspace'),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
           "TurboGears == 1.0.7",
           "SQLObject == 0.10.2",
           "formencode >= 0.7.1",
           "smbpasswd",
           #"syncer", 
	   "kid",
       	   "docutils",
           "TurboFeeds",
           "funkload",
           "pytz",
           "pycountry",
	   "nose",
           "BeautifulSoup",
           "mechanize",
           "whoosh",
           "pycha",
           "Mako",
           "httpagentparser",
           "html5lib",
           "vobject",
	   "pisa",
	   "reportlab",
	   "psycopg2"
      ],
      entry_points="""
[console_scripts]
run_hubspace = start_hubspace:main
export2ldap  = hubspace.sync.export2ldap:main
exportmissingusers2ldap = hubspace.sync.tools:exportMissingUsers2LDAP
sync_static = git_postmerge:main
      """,
      test_suite = 'nose.collector',
      )
