#!/bin/sh
#####################################################
version=5.2
description="Have Fun With NitroAdvancedHD Skin !!!"
#####################################################

TEMPATH='/tmp'
PLUGINPATH='/usr/lib/enigma2/python/Plugins/Extensions/NitroAdvanceFHD'
SKINPATH='/usr/share/enigma2/NitroAdvanceFHD'

CHECK='/tmp/check'
NITRO='/tmp/nitroadvancefhd/usr/*'
NITROSKIN='/tmp/nitroadvancefhd/share/*'

uname -m >$CHECK

# remove old version
rm -rf $PLUGINPATH >/dev/null 2>&1
rm -rf $SKINPATH >/dev/null 2>&1

cd $TEMPATH
set -e
wget -q https://raw.githubusercontent.com/biko-73/NitroAdvanceFHD/main/nitroadvancefhd-$version.tar.gz

tar -xzf nitroadvancefhd-"$version".tar.gz -C /tmp
set +e
rm -f nitroadvancefhd-"$version".tar.gz
cd ..

if grep -qs -i 'mips' cat $CHECK; then
        echo "[ Your device is MIPS ]"
elif grep -qs -i 'armv7l' cat $CHECK; then
        echo "[ Your device is armv7l ]"
elif grep -qs -i 'sh4' cat $CHECK; then
        echo "[ Your device is sh4 ]"
else
        echo "###############################"
        echo "## Your stb is not supported ##"
        echo "###############################"
        rm -r /tmp/nitroadvancefhd
        rm -f $CHECK
        exit 1
        echo ""
fi
echo "[ Installing New Skin Update Please Wait ... ]"
mkdir -p $PLUGINPATH
cp -r $NITRO $PLUGINPATH
mkdir -p $SKINPATH
cp -r $NITROSKIN $SKINPATH
sleep 2

rm -r /tmp/nitroadvancefhd
rm -f $CHECK

echo ""
sync
echo "#########################################################"
echo "#  NitroAdvanceFHD Skin $version INSTALLED SUCCESSFULLY #"
echo "#                BY BIKO - support on                   #"
echo "#   https://www.tunisia-sat.com/forums/forums/182/      #"
echo "#########################################################"
echo "#           your Device will RESTART Now                #"
echo "#########################################################"
killall -9 enigma2
exit 0
1