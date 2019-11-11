# holtek-prog.py

A Linux (Python) alternative to the Windows "Holtek USB Bridge Program" for use with the Holtek HT42B534 USB to UART Bridge IC (it might work with similar devices but this hasn't been tested).

**Warning** I couldn't find the spec to program the IC so the logic is based on monitoring what the Windows tool does. There are bugs, it doesn't catch all errors and sometimes when writing to the IC it fails and the settings are reset to the defaults (this also happens with the Windows tool).

# Installation

To use the tool you need to `apt install python3-usb` or equivalent.

# Usage

```
./holtek-prog.py -h
```

Shows a complete list of options available.

```
./holtek-prog.py 0x04d9 0xb534 -v 0x1234 -p 0x2345 -m "My Manufacturer" -d "My Description" -s "9876"
```

Look for a USB Device with Vendor ID 0x04d9, Product ID 0xb534 then sets the Vendor ID to 0x1234, Product ID to 0x2345, Manufacturer string, Description string and sets the Serial to 9876.

# Batch programming

```
./holtek-prog.py 0x04d9 0xb534 -v 0x1234 -p 0x2345 -m "My Manufacturer" -d "My Description" -s "9876" -L
```

When using "-L" the the tool waits for a device matching the VID/PID, programs it and then waits for the device to be removed before looking for another to program.

```
./holtek-prog.py 0x04d9 0xb534 -v 0x1234 -p 0x2345 -m "My Manufacturer" -d "My Description" -s "0028" -L -I -P
```

To give each device a unique serial number add "-I" to increment the serial after each write. Adding "-P" zero pads the serial number after being incremented otherwise the serial will be written as "0028" then "29".

<pre>
Waiting for device
 Device found
 Programming completed (Serial: 0028)
 Waiting for unplug
Waiting for device
 Device found
 Programming completed (Serial: 0029)
 Waiting for unplug
Waiting for device
 Device found
 Programming completed (Serial: 0030)
 Waiting for unplug
Waiting for device
 Device found
 Programming completed (Serial: 0031)
 Waiting for unplug
Waiting for device
...
</pre>

