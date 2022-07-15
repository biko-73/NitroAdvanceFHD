#!/bin/sh
##setup command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/biko-73/NitroAdvanceFHD/main/installerpiconCam_hdd.sh -O - | /bin/sh
## This script to downlaod and install Black Picon by () to inside skin

# Download and install Black Picons
cd /tmp
set -e
wget "https://github.com/biko-73/NitroAdvanceFHD//raw/main/piconCam_hdd.tar.gz"
tar -xzf piconCam_hdd.tar.gz -C /
set +e
cd ..

### delete tmp files
rm -f /tmp/piconCam_hdd.tar.gz
sync
echo ""
echo ""
echo "#########################################################"
echo "#               picon is downloaded                     #"
echo "#########################################################"
exit 0