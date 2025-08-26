gqrx-hamlib

startCAT.sh should be run at startup
LOG4OM2 can work with TCP on 4534 port

**Hamlib installation:**
mkdir ~/Project/hamlib
cd ~/Project/hamlib
wget https://github.com/Hamlib/Hamlib/releases/download/4.6.3/hamlib-4.6.3.tar.gz
tar -zxvf hamlib-4.6.3.tar.gz
cd hamlib-4.6.3
./configure --prefix=/usr/local --enable-static
make
sudo make install
sudo ldconfig

Copyright 2017 Simon Kennedy, G0FCU, g0fcu at g0fcu.com
