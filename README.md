# Kiwrious
A Pythion library for using the Kiwrious Sensors. Easy to install and use.


Install:
drop kiwrious.py where you would like to use it
install pyserial, `pip install pyserial`


Usage:
```
import kiwirous

sensor = kiwrious.Sensor()
```

then use `sensor.get_packet()` to return a dictanry of the sensor info

