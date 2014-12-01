#!/bin/sh

ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install python3
brew install qt
brew install sip --without-python --with-python3
brew install pyqt --without-python --with-python3

sudo pip3 install netifaces
sudo pip3 install gns3-gui
sudo pip3 install gns3-server

echo "Installing Dynamips 0.2.12"
curl -Lo dynamips http://sourceforge.net/projects/gns-3/files/Dynamips/0.2.12/dynamips-0.2.12-OSX.intel64.bin/download
chmod +x dynamips
sudo mv dynamips /usr/local/bin

echo "Installing VPCS 0.6"
curl -Lo vpcs http://sourceforge.net/projects/vpcs/files/0.6/vpcs_0.6_OSX64/download
chmod +x vpcs
sudo mv vpcs /usr/local/bin
