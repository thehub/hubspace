#!/bin/bash

python virtualenv.py --no-site-packages Deliverance
Deliverance/bin/easy_install pipDelivTest/bin/easy_install pip
Deliverance/bin/pip install http://deliverance.openplans.org/dist/Deliverance-snapshot-latest.pybundle
cp myrefs.py Deliverance/lib/python2.5/site-packages/
cp hubconfig.py Deliverance/lib/python2.5/site-packages/