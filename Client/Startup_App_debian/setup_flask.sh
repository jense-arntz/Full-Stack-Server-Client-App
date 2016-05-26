#!/bin/bash
chmod 777 -R /IIC-Client
apt-get install python
apt-get install build-essential
apt-get install python-dev python-pip
apt-get install requests sqlite python-sqlite
apt-get install daemon
pip install python-daemon
pip install netifaces
pip install exifread
apt-get install python-flask
apt-get install swig sqlite
pip install flask
apt-get install nginx uwsgi uwsgi-plugin-python
mkdir -p /camera/imgCap/single
mkdir -p /camera/imgCap/hdr3
mkdir -p /camera/imgCap/hdr5
chmod 777 -R /camera
chmod 777 -R /var
cd /tmp/
touch Client.sock
chown www-data Client.sock
cd /etc/nginx/sites-available
rm default
cp /IIC-Client/Client/Startup_App_debian/Client.conf /etc/nginx/sites-available/Client.conf
ln -s /etc/nginx/sites-available/Client.conf /etc/nginx/sites-enabled/Client.conf
cp /IIC-Client/Client/Startup_App_debian/Client.ini /etc/uwsgi/apps-available/Client.ini
ln -s /etc/uwsgi/apps-available/Client.ini /etc/uwsgi/apps-enabled/Client.ini
cd /IIC-Client/Client/Startup_App_debian
dos2unix ceeproxy_service.sh
cp /IIC-Client/Client/Startup_App_debian/ceeproxy_service.sh /etc/init.d/ceeproxy_service.sh
cd /etc/init.d
chmod +x ceeproxy_service.sh
update-rc.d ceeproxy_service.sh defaults
cd /IIC-Client/Client
sqlite3 Client.db < schema.sql
chmod 777 Client.db
cd
apt-get install libltdl-dev libusb-dev libusb-1.0 libexif-dev libpopt-dev
wget http://downloads.sourceforge.net/project/gphoto/libgphoto/2.5.7/libgphoto2-2.5.7.tar.gz
tar -xvzf libgphoto2-2.5.7.tar.gz
cd libgphoto2-2.5.7
./configure
make
make install
cd
git clone https://github.com/jim-easterbrook/python-gphoto2.git
cd python-gphoto2
python setup.py build_swig
python setup.py build
python setup.py install
reboot