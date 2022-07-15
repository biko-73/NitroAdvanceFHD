#!/bin/sh
##setup command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/biko-73/NitroAdvanceFHD/main/installerWhitePicons.sh -O - | /bin/sh
## This script to downlaod and install Black Picon by () to inside plugin

if [ ! -d /usr/lib64 ]; then
	PLUGINPATH=/usr/lib/enigma2/python/Plugins/Extensions/NitroAdvanceFHD
else
	PLUGINPATH=/usr/lib64/enigma2/python/Plugins/Extensions/NitroAdvanceFHD
fi

## Remove old file from tmp directory
[ -r /tmp/WhitePicons.tar.gz ] && rm -f /tmp/WhitePicons.tar.gz

### Remove Currenty file from plugin
rm -rf $PLUGINPATH/PICONS/emu
rm -rf $PLUGINPATH/PICONS/piconSat
rm -rf $PLUGINPATH/PICONS/piconProv
rm -rf $PLUGINPATH/PICONS/piconCrypt

# Download and install White Picons
cd /tmp
set -e
wget "https://github.com/biko-73/NitroAdvanceFHD//raw/main/WhitePicons.tar.gz"
tar -xzf WhitePicons.tar.gz -C /
set +e
cd ..

### delete tmp files
rm -f /tmp/WhitePicons.tar.gz
sync
echo ""
echo ""
echo "#########################################################"
echo "#       NitroAdvanceFHD INSTALLED SUCCESSFULLY          #"
echo "#                     By Biko                           #"              
echo "#                     support                           #"
echo "#  https://www.tunisia-sat.com/forums/threads/00000000  #"
echo "#########################################################"
echo ""
echo ""
echo "#########################################################"
echo "#            Press ok to Exit from Console              #"
echo "#########################################################"
exit 0
