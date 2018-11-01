# 1-10V Touch Dimmer
So this is a 1-10V dimmer controlled by an ESP32 with a touchkey.
The idea is for it to work like those bedside lamps that you touch
to control (bright -> dim -> off).
A 1-10V dimmer is just a variable resistor.
They often have a value of 80-100kOhm - I think - can't remember where I read that.
Anyways this project uses a set of relays to switch the circuit between Inf Ohm
(short circuit = off) -> ~25kOhm (Dimmed) -> 0 Ohm (full brightness).

I use an additional relay to control the stove lights.

## Component list

* ESP32 (wroom)
* Relay board