GNS3-gui
========

New GNS3 GUI repository (alpha stage).

Warning: this is not the repository for the stable version of GNS3 (0.8.6), please go to the gns3-legacy repository for it.

Linux/Unix
----------

Dependencies:

- Python version 3.3 or above
- pip & setuptools must be installed, please see http://pip.readthedocs.org/en/latest/installing.html
  (or sudo apt-get install python3-pip but install more packages)
- PyQt must be installed, to install on Debian-like Linux: sudo apt-get install python3-pyqt4
- Dynamips version 0.2.11 or above (http://github.com/GNS3/dynamips)

.. code:: bash

   cd gns3-gui-master
   sudo python3 setup.py install
   gns3

`Detailed instructions for Debian Jesse <http://forum.gns3.net/topic8988.html>`_. 

Windows
-------

Please use our all-in-one installer.

Mac OS X
--------

DMG package is not available yet.

You can manually install using the following steps (experimental):

First install homebrew `http://brew.sh/`_.

Then install GNS3 dependencies.

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
