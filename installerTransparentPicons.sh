#!/bin/sh
##setup command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/biko-73/NitroAdvanceFHD/main/installerTransparentPicons.sh -O - | /bin/sh
## This script to downlaod and install Black Picon by () to inside plugin

if [ ! -d /usr/lib64 ]; then
	PLUGINPATH=/usr/lib/enigma2/python/Plugins/Extensions/NitroAdvanceFHD
else
	PLUGINPATH=/usr/lib64/enigma2/python/Plugins/Extensions/NitroAdvanceFHD
fi

mkdir -p $PLUGINPATH/PICONS

### Checking if picons folder avinable on plugin
if [ ! -d $PLUGINPATH/PICONS/emu ]; then
	echo "Missing emu folder will be send it to plugin path"
	cp -r $PLUGINPICONTMPPATH/emu $PLUGINPATH/PICONS > /dev/null 2>&1
else
	cp -u $PLUGINPICONTMPPATH/emu/* $PLUGINPATH/PICONS/emu > /dev/null 2>&1
fi
if [ ! -d $PLUGINPATH/PICONS/piconProv ]; then
	echo "Missing piconProv folder will be send it to plugin path"
	cp -r $PLUGINPICONTMPPATH/piconProv $PLUGINPATH/PICONS > /dev/null 2>&1
else
	cp -u $PLUGINPICONTMPPATH/piconProv/* $PLUGINPATH/PICONS/piconProv > /dev/null 2>&1
fi
if [ ! -d $PLUGINPATH/PICONS/piconSat ]; then
	echo "Missing piconSat folder will be send it to plugin path"
	cp -r $PLUGINPICONTMPPATH/piconSat $PLUGINPATH/PICONS > /dev/null 2>&1
else
	cp -u $PLUGINPICONTMPPATH/piconSat/* $PLUGINPATH/PICONS/piconSat > /dev/null 2>&1
fi
if [ ! -d $PLUGINPATH/PICONS/piconCrypt ]; then
	echo "Missing piconCrypt folder will be send it to plugin path"
	cp -r $PLUGINPICONTMPPATH/piconCrypt $PLUGINPATH/PICONS > /dev/null 2>&1
else
	cp -u $PLUGINPICONTMPPATH/piconCrypt/* $PLUGINPATH/PICONS/piconCrypt > /dev/null 2>&1
fi

# Download and install Transparent Picons
cd /tmp
set -e
wget "https://github.com/biko-73/NitroAdvanceFHD//raw/main/TransparentPicons.tar.gz"
tar -xzf TransparentPicons.tar.gz -C /
set +e
cd ..

### delete tmp files
rm -f /tmp/TransparentPicons.tar.gz
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
