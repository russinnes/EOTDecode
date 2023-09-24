# EOTDecode

A lightweight linux python-based decoder for real-time End-Of-Train data 

## Background

I was working on a separate project examining a theoretical generated/replay attack on automated railway equipment, primarily the end-of-train device which has control of emergency braking. The equipment in use is susceptible to a UHF broadcast using FSK modulation at 1200bps. An easily crafted data packet could transmit malicious messages to the receiver and action the device. In researching the messaging bit pattern, it became clear there is a niche group of railroad enthusiasts who like to decode the status broadcast messages from the "End of Train" devices. Apparently software that does this is hard-to-come-by, aside from a closed-source windows tool which is restricted by it's developers. I figured - it's just decoding 1200bps FSK, we can do that really easily if we string together a few existing tools. 

## History of this tool
A deeper look at the existing software seemed to require radio scanners, piping audio through virtual patch cables, in some cases piping audio between something like GQRX and a virtual source, and it was all windows-based. 

I really like using SDR's for quick, cheap access to the RF spectrum. They make easy work of piping samples on to other things. The Minimodem tool from [Kamal Mostafa](https://github.com/kamalmostafa) has been around for some time, and provides easy (albeit basic) demodulation of old-school modulation schemes. We can also specify our own mark/space frequencies. By configuring Minimodem to output demodulated raw 8-bit data, perhaps we could easily start decoding the bit strings. 

The only real hangup was that Minimodem is designed to take in samples from an audio source - while we could do this while still using an SDR and piping audio out and back in, using loopback devices etc, it seemed really messy and unnecessary. Planning on writing some new code for Minimodem to support input via stdin (odd to me that it didn't to begin with?), I decided to see if anyone else had, and luckily found [this](https://github.com/kamalmostafa/minimodem/pull/56) unmerged PR from [Erhannis](https://github.com/Erhannis) to the master branch of Minimodem. 

RTL_FM produces signed, 16-bit integers, with Multimodem requiring floats. The endlessly-powerfull SoX tool will happily convert to our required float when inserted into the pipeline. After compiling the stdio branch, I fed it with a random FSK source from RTL_FM and voila! - we're outputting a bit string. The only issue (less than ideal) is the output is a string datatype, but that's still workable. 

In my travels through github, I found a function from [Eric Reuter](https://github.com/ereuter) which he presented at DEFCON 26 which really made things easy. It can be found [here]. He was bringing in data from GNU Radio but that seems unnecessary for most folks. (https://github.com/ereuter/PyEOT). 

## Signal processing workflow
* Tune RTL_FM to 457.9375 and pipe raw samples to SoX
* SoX - read samples as S16_LE and output floating-point at 48000Hz
* Minimodem configured for 1200Hz/1800Hz at 1200bps and writing out single bits
* Process the bitstring
* Profit

### Dependencies
All dependencies will be installed using the ./install.sh script, but include:
* cmake, pkg-config, sox, build-essential, automake, autoconf
* rtl_sdr, libusb-1.0-0-dev
* minimodem (with stdin support) [on my github found here](https://github.com/russinnes/minimodem-stdio)

### Installing
The included install script will bring in everything you need, no need to source other dependencies.
```
cd ~/
git clone https://github.com/russinnes/EOTDecode.git
cd EOTDecode
chmod +x install.sh
./install.sh
```

### Get PPM value of your sdr
```
rtl_test -p (wait a few minutes and write it down)
edit ~/EOTDecode/EOTconfig.py and change the PPM value to the one you noted earlier

*Note* - You will have to experiment with gain value (0-48) in the config file, I had good results with "None" (auto)


```
### Executing program
```
cd ~/EOTDecode
./EOTdecode.py
```

## Sample output
```
./EOTdecode.py 
Using RTL SDR as input source

Found 2 device(s):
  0:  Realtek, RTL2838UHIDIR, SN: 10
  1:  Realtek, RTL2838UHIDIR, SN: 20

Using device 1: Generic RTL2832U OEM
Found Rafael Micro R820T tuner
Tuner gain set to automatic.
Tuner error set to 8 ppm.
Tuned to 458189500 Hz.
Oversampling input by: 21x.
Oversampling output by: 1x.
Buffer size: 8.13ms
Exact sample rate is: 1008000.009613 Hz
Allocating 15 zero-copy buffers
Sampling at 1008000 S/s.
Output at 48000 Hz.


EOT 2023-09-20 10:38:34.258
---------------------
Unit Address:   39351
Pressure:       87 psig
Motion:         1
Marker Light:   1
Turbine:        1
Battery Cond:   OK
Battery Charge: 0%
Arm Status:     Normal
```
The same data is dumped as JSON to a log file in the working directory as well. 

This project is licensed under the MIT license.

## Acknowledgments

Code snippets from:
* [Eric Reuter](https://github.com/ereuter) 
* [erhannis](https://github.com/Erhannis/minimodem/tree/feature/stdio) for saving me time with his minimodem stdin fork
