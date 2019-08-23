Flavour addon manager for the Divio Cloud addon system
======================================================

FAM for supporting old style Divio Cloud addons.

required install attributes
---------------------------

* artifact - url to the packag
* addon_name - name of the addon


action: add
-------------


action: remove
--------------

It will NOT delete the files in the `templates` and `static` folder which got installed during the `add` action. These file might have changed and should be manually removed.

It will update the `settings.py`, ...
