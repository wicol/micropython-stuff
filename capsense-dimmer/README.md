So this is a 1-10V dimmer controlled by an ESP32 with a touchkey.
A 1-10V dimmer is just a variable resistor.
They often have a value of 80-100kOhm - I think - can't remember where I read that.
Anyways the MCP4110 used here is 100kOhm so it should work fine.

Component list:

* ESP32 (wroom)
* MCP4110 (digital pot with SPI interface)
