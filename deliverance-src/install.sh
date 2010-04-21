#!/bin/bash

python virtualenv.py --no-site-packages Deliverance
Deliverance/bin/easy_install pipDelivTest/bin/easy_install pip
Deliverance/bin/pip install http://deliverance.openplans.org/dist/Deliverance-snapshot-latest.pybundle
pwd2=`pwd` 
ln -s ${pwd2}/../hubspace ./Deliverance/lib/python2.5/site-packages/hubspace
ln -s ${pwd2}/myrefs.py ./Deliverance/lib/python2.5/site-packages/myrefs.py