# Agilent_8000A_Series_Infiniium_Oscilloscopes
Transfer formatted waveform data for analog channels to a computer.

Tested on Agilent MSO8104A Infiniium Oscilloscope.

## Requirements:

- Python 3.4+
- `pyVISA` >1.6

    You can install it using pip:
    ```bash
    $ pip install -U pyvisa
    ```
- `NI VISA 17.5`

	[Download NI-VISA for Windows](http://www.ni.com/download/ni-visa-17.5/7224/en/ "NI-VISA 17.5 for Windows")

	[Download NI-VISA for Mac OS X](http://www.ni.com/download/ni-visa-17.5/7220/en/ "NI-VISA 17.5 for Mac")
    
	[Download NI-VISA for Linux](http://www.ni.com/download/ni-visa-17.0/6700/en/ "NI-VISA 17.5 for Linux")

## Usage:

- modified the parameters in the init() function
- modified storage depth and sample rate in the main() function
- RUN!
