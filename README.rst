GNS3-gui
========

.. image:: https://travis-ci.org/GNS3/gns3-gui.svg?branch=master
    :target: https://travis-ci.org/GNS3/gns3-gui

.. image:: https://img.shields.io/pypi/v/gns3-gui.svg
    :target: https://pypi.python.org/pypi/gns3-gui


GNS3 GUI repository.

Linux (Debian based)
--------------------

The following instructions have been tested with Ubuntu and Mint.
You must be connected to the Internet in order to install the dependencies.

Dependencies:

- Python 3.3 or above
- Setuptools
- PyQt libraries
- Apache Libcloud library
- Requests library
- Paramiko library

The following commands will install some of these dependencies:

.. code:: bash

   sudo apt-get install python3-setuptools
   sudo apt-get install python3-pyqt4

Finally these commands will install the GUI as well as the rest of the dependencies:

.. code:: bash

   cd gns3-gui-master
   sudo python3 setup.py install
   gns3

Windows
-------

Please use our `all-in-one installer <https://community.gns3.com/community/software/download>`_ to install the stable build.

If you install via source you need to first install:

- Python (3.3 or above) - https://www.python.org/downloads/windows/
- Pywin32 - https://sourceforge.net/projects/pywin32/
- Qt4 - http://www.qt.io/download-open-source/
- PyQt4 - http://www.riverbankcomputing.com/software/pyqt/download
- PyCrypto (which if you compile from source, requires Visual Studio 2010 with GMP or MPIR libraries)

And finally, call

.. code:: bash

   python setup.py install

to install the remaining dependencies.

Mac OS X
--------

Please use our DMG package or you can manually install using the following steps (experimental):

`First install homebrew <http://brew.sh/>`_.

Then install the GNS3 dependencies.

.. code:: bash

   brew install python3
   brew install qt
   brew install sip --without-python --with-python3
   brew install pyqt --without-python --with-python3

Finally, install both the GUI & server from the source.

.. code:: bash

   cd gns3-gui-master
   python3 setup.py install

.. code:: bash

   cd gns3-server-master
   python3 setup.py install

Or follow this `HOWTO that uses MacPorts <http://binarynature.blogspot.ca/2014/05/install-gns3-early-release-on-mac-os-x.html>`_.

Developement
-------------

If you want to update the interface, modify the .ui files using QT tools. And:

.. code:: bash

    cd scripts
    python build_pyqt.py
