#!/bin/sh
##setup command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/biko-73/NitroAdvanceFHD/main/installerWhitePicons.sh -O - | /bin/sh

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
echo "#               picon is downloaded                     #"
echo "#########################################################"
exit 0
