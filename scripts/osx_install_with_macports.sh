#!/bin/sh

if [ ! -f /usr/bin/clang ]; then
    echo "Please install Xcode Command Line Developer Tools"
    xcode-select --install
    exit
fi

if [ ! -f /opt/local/bin/port ]; then
    echo "Please install MacPorts: https://www.macports.org/install.php"
    exit
fi

source $HOME/.profile
sudo port -v install py34-pyqt4 py34-zmq py34-pip

sudo pip-3.4 install netifaces
sudo pip-3.4 install gns3-gui
sudo pip-3.4 install gns3-server

echo "PATH=/opt/local/bin:/opt/local/sbin:/opt/local/Library/Frameworks/Python.framework/Versions/3.4/bin:$PATH" >> $HOME/.profile
source $HOME/.profile

echo "Installing Dynamips 0.2.12"
curl -Lo dynamips http://sourceforge.net/projects/gns-3/files/Dynamips/0.2.12/dynamips-0.2.12-OSX.intel64.bin/download
chmod +x dynamips
sudo mv dynamips /opt/local/bin

echo "Installing VPCS 0.6"
curl -Lo vpcs http://sourceforge.net/projects/vpcs/files/0.6/vpcs_0.6_OSX64/download
chmod +x vpcs
sudo mv vpcs /opt/local/bin
