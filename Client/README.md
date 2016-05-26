# Setup Client App

You must login system as root. 

## Debian

Installation
============
### To deploy the Client App on device, use git to "clone" the Github repository.
    
    cd /
    git clone https://github.com/ceecam/IIC-Client
    
### To install development environment, run setup_flask.sh file.
    
    apt-get install tofrodos
    ln -s /usr/bin/fromdos /usr/bin/dos2unix
    cd /IIC-Client/Client/Startup_App_debian
    dos2unix setup_flask.sh
    sh setup_flask.sh
    
### Start servers.
    
    service nginx restart
    service uwsgi restart
    /etc/init.d/ceeproxy_service.sh start
    
    
## Arch Linux

Installation
============
### To deploy the Client App on device, use git to "clone" the Github repository.
    
    pacman -S git
    cd /
    git clone https://github.com/ceecam/IIC-Client    

### To install development environment, run setup_flask.sh file.

    cd /IIC-Client/Client/Startup_App_Arch
    pacman -S dos2unix
    dos2unix setup_flask.sh
    sh setup_flask.sh
    
### Start servers.
    systemctl restart nginx.service 
    systemctl restart uwsgi.service
    systemctl start ceeproxy.service 

    

    
    