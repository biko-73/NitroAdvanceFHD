#!/bin/sh
##setup command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/biko-73/NitroAdvanceFHD/main/installerBlackPicons.sh -O - | /bin/sh
## This script to downlaod and install Black Picon by () to inside skin

# Download and install Black Picons
cd /tmp
set -e
wget "https://github.com/biko-73/NitroAdvanceFHD//raw/main/BlackPicons.tar.gz"
tar xzvpf /tmp/BlackPicons.tar.gz  -C / 
set +e
cd ..

### delete tmp files
rm -f /tmp/BlackPicons.tar.gz
sync
echo ""
echo ""
echo "#########################################################"
echo "#               picon is downloaded                     #"
echo "#########################################################"