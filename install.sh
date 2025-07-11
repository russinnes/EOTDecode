#!/bin/bash
echo "====== Installing dependancies - please enter sudo password when prompted"
sleep 1

cd
mkdir EOTDecode_temp; cd EOTDecode_temp

echo "====== Updating APT packages"
sudo apt update

echo "====== Installing required build tools"
sudo apt install git cmake pkg-config libusb-1.0-0-dev sox
sudo apt install build-essential automake autoconf
sudo apt install libsndfile1-dev fftw3-dev libfftw3-dev libasound2-dev libpulse-dev libsndio-dev

echo "====== Checking for RTL_FM"

if type rtl_fm >/dev/null 2>&1; then
    echo "====== RTL_FM already exists"

else
    echo "====== RTL_FM does not exist - fetching source"
    echo ""
    #git clone git://git.osmocom.org/rtl-sdr.git
    # Updated git as per #1
    git clone https://gitea.osmocom.org/sdr/rtl-sdr.git
    
    cd rtl-sdr; mkdir build; cd build
    cmake ../ -DINSTALL_UDEV_RULES=ON
    make; sudo make install
    sudo cp ../rtl-sdr.rules /etc/udev/rules.d/
    sudo ldconfig

    # blacklist rtl dtv drivers
    if [ ! -f /etc/modprobe.d/blacklist-rtl.conf ]; then
        echo "====== Installing blacklist-rtl.conf"
        echo "====== Please reboot before running this"
        sudo install -m 0644 ~/EOTDecode/blacklist-rtl.conf /etc/modprobe.d/
        sudo ldconfig
    fi

    echo "====== RTL-SDR installation complete - cleaning up"
    echo ""
    
fi


echo "====== Installing SoX"
sudo apt install sox


# Minimodem
echo "====== Installing MiniModem build with STDIO support"
cd ~/EOTDecode_temp/
git clone https://github.com/russinnes/minimodem-stdio.git --branch stdio
cd minimodem-stdio
autoreconf --install; ./configure; make; sudo make install
echo "====== MiniModem (STDIO build) installation complete - cleaning up"
sudo rm -rf ~/EOTDecode_temp
cd ~/EOTDecode
chmod +x EOTdecode.py
echo "====== Installation complete"
echo ""
echo "====== EOTDecode can be launched in ~/EOTDecode/EOTdecode.py"
echo "====== Please configure SDR variables in ~/EOTDecode/EOTconfig.py prior to use"





