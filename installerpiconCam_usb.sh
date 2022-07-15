#!/bin/sh
##setup command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/biko-73/NitroAdvanceFHD/main/installerpiconCam_usb.sh -O - | /bin/sh
## This script to downlaod and install Black Picon by () to inside skin

# Download and install Black Picons
cd /tmp
set -e
wget "https://github.com/biko-73/NitroAdvanceFHD//raw/main/piconCam_usb.tar.gz"
tar -xzf piconCam_usb.tar.gz -C /
set +e
cd ..

### delete tmp files
rm -f /tmp/piconCam_usb.tar.gz
sync
echo ""
echo ""
echo "#########################################################"
echo "#               picon is downloaded                     #"
echo "#########################################################"
exit 0