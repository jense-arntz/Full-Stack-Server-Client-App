#!/bin/bash
pacman -Syu nginx uwsgi python2-flask sqlite
pacman -Syu uwsgi-plugin-python
mkdir -p /camera/imgCap/single
mkdir -p /camera/imgCap/hdr3
mkdir -p /camera/imgCap/hdr5
chmod 777 -R /camera
chmod 777 -R /var
chmod 777 -R /IIC-Client
pacman -S python-dev python-pip
pacman -S requests
pacman -S build-essential
pip install flask
pip install exifread
pip install netifaces
pacman -S daemon
pip install python-daemon
pacman -S swig
cp /IIC-Client/Client/Startup_App_Arch/uwsgi.service /etc/systemd/system/uwsgi.service
cp /IIC-Client/Client/Startup_App_Arch/nginx.conf /etc/nginx/nginx.conf
cp /IIC-Client/Client/Startup_App_Arch/ceeproxy.service /etc/systemd/system/ceeproxy.service
systemctl enable ceeproxy.service
systemctl enable uwsgi.service
cd /IIC-Client/Client
sqlite3 Client.db < schema.sql
chmod 777 Client.db
cd
pacman -S libltdl-dev libusb-dev libusb-1.0 libexif-dev libpopt-dev
wget http://downloads.sourceforge.net/project/gphoto/libgphoto/2.5.7/libgphoto2-2.5.7.tar.gz
tar -xvzf libgphoto2-2.5.7.tar.gz
cd libgphoto2-2.5.7
./configure
make
sudo make install
git clone https://github.com/jim-easterbrook/python-gphoto2.git
cd python-gphoto2
python setup.py build_swig
python setup.py build
python setup.py install
reboot