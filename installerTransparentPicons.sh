#!/bin/sh
##setup command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/biko-73/NitroAdvanceFHD/main/installerTransparentPicons.sh -O - | /bin/sh
## This script to downlaod and install Black Picon by () to inside plugin

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
echo "#               picon is downloaded                     #"
echo "#########################################################"
exit 0
