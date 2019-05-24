GNS3-gui
========

.. image:: https://travis-ci.org/GNS3/gns3-gui.svg?branch=master
    :target: https://travis-ci.org/GNS3/gns3-gui

.. image:: https://img.shields.io/pypi/v/gns3-gui.svg
    :target: https://pypi.python.org/pypi/gns3-gui


GNS3 GUI repository.

Installation
------------

Please see https://docs.gns3.com/

Development
-------------

If you want to update the interface, modify the .ui files using QT tools. And:

.. code:: bash

    cd scripts
    python build_pyqt.py

Debug
"""""

If you want to see the full logs in the internal shell you can type:

.. code:: bash
    
    debug 2


Or start the app with --debug flag.

Due to the fact PyQT intercept you can use a web debugger for inspecting stuff:
https://github.com/Kozea/wdb

Security issues
----------------
Please contact us using contact informations available here:
http://docs.gns3.com/1ON9JBXSeR7Nt2-Qum2o3ZX0GU86BZwlmNSUgvmqNWGY/index.html

