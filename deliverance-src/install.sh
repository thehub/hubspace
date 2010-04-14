#!/usr/bin/python

python virtualenv.py --no-site-packages Deliverance
Deliverance/bin/easy_install pipDelivTest/bin/easy_install pip
Deliverance/bin/pip install http://deliverance.openplans.org/dist/Deliverance-snapshot-latest.pybundle
Deliverance/bin/paster create -t deliverance Deliverance