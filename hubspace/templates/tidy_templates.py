#!/usr/bin/python2.4
import sys
import tidy
from BeautifulSoup import BeautifulSoup
from glob import glob
from os import path, rename
options = dict(output_xhtml=0, indent=1, indent_spaces=2, tidy_mark=0)

def tidy_templates():
    for file_name in glob('*.kid'):
        #back up the old file
        old = open(file_name)
        untidy = open(file_name + '.untidied', 'w')
        untidy.write(old.read())
        untidy.close()
        old.close()
        #tidied = tidy.parse(file_name, **options)
        soup = BeautifulSoup(open(file_name).read())
        pretty = soup.prettify()
        #errors = tidied.error
        tidied = open(file_name, 'w') # not sure why we need this but otherwise the doc ends up empty
        tidied.write(pretty)
    for file_name in glob('*.kid'):
        old_file = open(file_name)
        old = old_file.read()
        old = old.replace('??>', '?>')
        old_file.close()
        new = open(file_name, 'w')
        print `old`
        new.write(old)
        new.close()
	

def revert_tidy():
    for file_name in glob('*.kid.untidied'):
        oldname = file_name.rsplit('.', 1)[0]
        revert = open(oldname, 'w')
        old = open(file_name)
        revert.write(old.read())
        revert.close()
        old.close()

if 'tidy' in sys.argv:
    tidy_templates()
else:
    revert_tidy()
