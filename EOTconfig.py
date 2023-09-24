'''
Config parameters for EOTdecode.py
'''

# Set to True if using an RTL SDR dongle for RF input, False if using soundcard input
USE_RTL = True

# RTL Frequency
FREQ = '457.9375M'
# RTL Device Number, usually 0 if only a single device is plugged in.
DEVICE = 0

# RTL PPM Value (Can be found utin rtl_test -p , wait a few minutes to get a stable value)
PPM = 8

# Desired gain, leave as None for automatic gain
GAIN = None
