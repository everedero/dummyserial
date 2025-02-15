# Python Module for Dummy Serial

Emulates pyserial's write/read responses from a serial port.

## Install

    pip3 install dummyserial

## Usage

Instead of:

    from serial import Serial

Use:

    from dummyserial import Serial

It is possible to use the MonkeyPatch package:
```
from pytest import MonkeyPatch
import dummyserial
import lookup_mock
monkeypatch.setattr("dummyserial.lookup.default", lookup_mock.default)
monkeypatch = MonkeyPatch()
monkeypatch.setattr("serial.Serial", dummyserial.Serial)
```
Then you can call your application main function, and every call to the serial.Serial object
will be replaced by a dummyserial.Serial call as if you had a monkey in a production line
exchanging one object for another. This allows you to execute tests without modifying anything in the
application code.

Don’t forget that this will only work if you monkeypatch before you
call any other module from your application.

### Implement look-up functions
This version uses a look-up function instead of a table.

A lookup function has to take as input a string representing the UART command,
and a default invalid parameter.
It has to return either a string or a bytes string.

Exemple of lookup, always returning byte 0:
```
def exemple(in_str, ans_when_invalid):
    out_str = b"\x00"
    return(out_str)
```

In order to use the new lookup, you can either open the serial port with the optional "lookup" argument:

    ser = dummyserial.Serial("dev/ttyUSB0", lookup=myfunc)

Or you can override it with MonkeyPatch, in order to have your lookup function live in the same test directory
as the project you need UART mocking for.

```
from pytest import MonkeyPatch
monkeypatch = MonkeyPatch()
import custom_lookup
monkeypatch.setattr("dummyserial.lookup.default", custom_lookup.default)
import dummyserial
monkeypatch.setattr("serial.Serial", dummyserial.Serial)
```

The order matters and the lookup override has to take place before the dummy module import.

# Source
This is a fork of https://github.com/Victor-Chavanne/dummyserial.git which is a fork of https://github.com/ampledata/dummyserial.

## Authors
* 'dummyserial' Stand-alone Python Module: Greg Albrecht <gba@orionlabs.io>
* 'dummy\_serial.py' Mock Fixture: Jonas Berg <pyhys@users.sourceforge.net>

## Copyright
Copyright 2016 Orion Labs, Inc.

## License
Apache License, Version 2.0
