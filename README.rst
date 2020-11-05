GNS3-gui
========

.. image:: https://github.com/GNS3/gns3-gui/workflows/testing/badge.svg
    :target: https://github.com/GNS3/gns3-gui/actions?query=workflow%3Atesting

.. image:: https://img.shields.io/pypi/v/gns3-gui.svg
    :target: https://pypi.python.org/pypi/gns3-gui

.. image:: https://snyk.io/test/github/GNS3/gns3-gui/badge.svg
    :target: https://snyk.io/test/github/GNS3/gns3-gui


GNS3 GUI repository.

Installation
------------

Please see https://docs.gns3.com/

Software dependencies
---------------------

PyQt5 which is either part of the Linux distribution or installable from PyPi. The other Python dependencies are automatically installed during the GNS3 GUI installation and are listed `here <https://github.com/GNS3/gns3-gui/blob/master/requirements.txt>`_

For connecting to nodes using Telnet, a Telnet client is required. On Linux that's a terminal emulator like xterm, gnome-terminal, konsole plus the telnet program. For connecting to nodes with a GUI, a VNC client is required, optionally a SPICE client can be used for Qemu nodes.

For using packet captures within GNS3, Wireshark should be installed. It's recommended, but if you don't need that functionality you can go without it.

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

Please contact us at security@gns3.net


