Working with message catalogues
===============================

Overview
--------

Customizing messages/text appearing in hubspace application is a three step process

- Download message catalogue file
- Use Poedit to add translation, change messages
- Send changed catalogue file back

 
Get the .po file
----------------

Message catalogue (.po file) are the file that contain strings and their translations used in software,

- Login to hubspace http://members.the-hub.net
- Go to Hosting Tab. Select Administration
- Check Messages section.
- Click on Download link in Translation subsection

 
Using Poedit
------------

Poedit is cross-platform gettext catalogs (.po files) editor.
 
Install
~~~~~~~~~~

If you are using Ubuntu, type following in terminal window

    sudo apt-get install poedit


In case you are using other Operating Systems refer the instructions at http://www.poedit.net/download.php

 
Prefernces
~~~~~~~~~~

When you start Poedit for the first time it asks you a couple of question so that it adds your information to catalogue revisions.

Now set preferences: Click on edit-> Preferences and make sure you set preference like shown below.

POEdit Preferences: Screenshot 
  .. image:: images/Screenshot-Preferences.png
     :scale: 50

Unchecking first option about automatic .mo compiling is important


Editing
~~~~~~~

Editing messages is very easy.

You must however remember a few things

    * % sign has a special significance. "%()s" around a text is treated for text substitution by the software.

      Such wrapped text should not be translated.

      For example in some messages %(location_name)s is replaced by name of the hub in the conext. So text like "Welcome to %(location_name)s" will be replaced by "Welcome to Madrid" for hub Madrid.
          o Please note that %(location_name)s is however NOT available for all messages.
    * If you want to use % sign use it escaped by adding an extra %.

      Eg. 50% should be would be 50%%
    * \n characters indicates newlines in some cases. Such as welcome mail template
 

You can search for specific message and add your translation/change.

 
POEdit Editing: Screenshot 
  .. image:: images/Screenshot-Poedit.png
     :scale: 50

 
Send the changes
----------------

Now save and send the modified file back to world.tech.space@the-hub.net .
