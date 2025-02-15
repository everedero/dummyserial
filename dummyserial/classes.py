#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Dummy Serial Class Definitions"""

import logging
import logging.handlers
import sys
import time

from serial import SerialException, PortNotOpenError

import dummyserial.constants
import dummyserial.lookup as lookup

__author__ = 'Greg Albrecht <gba@orionlabs.io>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


class Serial():
    """
    Dummy (mock) serial port for testing purposes.

    Mimics the behavior of a serial port as defined by the
    `pySerial <https://github.com/pyserial/pyserial>`_ module.

    Args:
        * port:
        * timeout:

    Note:
    As the portname argument not is used properly, only one port on
    :mod:`dummyserial` can be used simultaneously.
    """

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(dummyserial.constants.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(dummyserial.constants.LOG_LEVEL)
        _console_handler.setFormatter(dummyserial.constants.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, *args, **kwargs):
        self._logger.debug('args=%s', args)
        self._logger.debug('kwargs=%s', kwargs)

        self.is_open = True
        self._waiting_data = dummyserial.constants.NO_DATA_PRESENT

        self.baudrate = kwargs.get("baudrate") # None if key not found
        if (self.baudrate == None and len(args) > 1):
            self.baudrate = args[1]
        else:
            self._logger.warn('No baudrate provided, using default')
            self.baudrate = dummyserial.constants.DEFAULT_BAUDRATE

        self.port = kwargs.get("port")
        if (self.port == None and len(args) > 0):
            self.port = args[0]
        else:
            raise IOError("No port provided")

        self.initial_port_name = self.port  # Initial name given to the port

        self.lookup = kwargs.get(
            'lookup', lookup.default)
        self.lookup_func = lookup.default
        self.timeout = kwargs.get(
            'timeout', dummyserial.constants.DEFAULT_TIMEOUT)
        self.writeTimeout = self.timeout

    def __repr__(self):
        """String representation of the DummySerial object."""
        return (
            f"{self.__module__}."
            f"{self.__class__.__name__}"
            f"<id=0x{id(self):x}, "
            f"open={self.is_open}"
            f">(port={self.port}, "
            f"timeout={self.timeout}, "
            f"waiting_data={self._waiting_data})"
        )

    def open(self):
        """Open a (previously initialized) port."""
        self._logger.debug('Opening port')

        if self.is_open:
            raise SerialException('Port is already open.')

        self.is_open = True
        self.port = self.initial_port_name

    def close(self):
        """Close a port on dummy_serial."""
        self._logger.debug('Closing port')
        if self.is_open:
            self.is_open = False
        self.port = None

    def write(self, data):
        """
        Write to a port on dummy_serial.

        Args:
            data (string/bytes): data for sending to the port on
            dummy_serial. Will affect the response for subsequent read
            operations.

        Note that for Python2, the inputdata should be a **string**. For
        Python3 it should be of type **bytes**.
        """
        self._logger.debug('Writing (%s): "%s"', len(data), data)

        if not self.is_open:
            raise PortNotOpenError

        if sys.version_info[0] > 2:
            if not isinstance(data, bytes):
                raise dummyserial.exceptions.DSTypeError(
                    'The input must be type bytes. Given:' + repr(data))
            input_str = str(data, encoding='latin1')
        else:
            input_str = data

        # Look up which data that should be waiting for subsequent read
        # commands.
        self._waiting_data = self.lookup_func(input_str, dummyserial.constants.DEFAULT_RESPONSE)

    def read(self, size=1):
        """
        Read size bytes from the Dummy Serial Responses.

        The response is dependent on what was written last to the port on
        dummyserial, and what is defined in the :data:`RESPONSES` dictionary.

        Args:
            size (int): For compability with the real function.

        Returns a **string** for Python2 and **bytes** for Python3.

        If the response is shorter than size, it will sleep for timeout.

        If the response is longer than size, it will return only size bytes.
        """
        self._logger.debug('Reading %s bytes.', size)

        if not self.is_open:
            raise PortNotOpenError

        if size < 0:
            raise dummyserial.exceptions.DSIOError(
                ('The size to read must not be negative. '
                f'Given: {size}'))

        # Do the actual reading from the waiting data, and simulate the
        # influence of size.
        if self._waiting_data == dummyserial.constants.DEFAULT_RESPONSE:
            return_str = self._waiting_data
        elif size == len(self._waiting_data):
            return_str = self._waiting_data
            self._waiting_data = dummyserial.constants.NO_DATA_PRESENT
        elif size < len(self._waiting_data):
            self._logger.debug(
                'The size (%s) to read is smaller than the available data. ' +
                'Some bytes will be kept for later. ' +
                'Available (%s): "%s"',
                size, len(self._waiting_data), self._waiting_data
            )

            return_str = self._waiting_data[:size]
            self._waiting_data = self._waiting_data[size:]
        else:  # Wait for timeout - we asked for more data than available!
            self._logger.debug(
                'The size (%s) to read is larger than the available data. ' +
                'Will sleep until timeout. ' +
                'Available (%s): "%s"',
                size, len(self._waiting_data), self._waiting_data
            )

            time.sleep(self.timeout)
            return_str = self._waiting_data
            self._waiting_data = dummyserial.constants.NO_DATA_PRESENT

        self._logger.debug(
            'Read (%s): "%s"',
            len(return_str), return_str
        )

        if sys.version_info[0] > 2:  # Convert types to make it python3 compat.
            if type(return_str) == str:
                return bytes(return_str, encoding='latin1')
            elif type(return_str) == bytes:
                return(return_str)
            else:
                print(type(return_str))
                print(return_str)
                raise IOError("Invalid return type in lookup func")
        return return_str

    def out_waiting(self):  # pylint: disable=C0103
        """Returns length of waiting output data."""
        return len(self._waiting_data)

    def isOpen(self):  # pylint: disable=C0103
        """Return wheather or not the connection is open"""
        return self.is_open

    def flushInput(self):
        """Flushes input"""
        self._logger.debug("Input flush")

    def flush(self):
        """Flushes input and output"""
        self._logger.debug("Complete flush")
        self._waiting_data = dummyserial.constants.NO_DATA_PRESENT

    def flushOutput(self):
        """Flushes output"""
        self._logger.debug("Output flush")
        self._waiting_data = dummyserial.constants.NO_DATA_PRESENT

    def fileno(self):
        self._logger.warn("fileno is used but is not multiplatform")
        return 1

    def inWaiting(self):
        """
        Always instant because the module is fake
        """
        return False

    def readline(self, size=None):
        """
        Read until b'\n'.
        Older version have a size arguments but that is wrong
        """
        if size != None:
            self._logger.warn("readline should not have an argument")
            return(self.read(size))

        stop = False
        bstr = b''
        self._logger.setLevel(logging.WARN)
        while not stop:
            char = self.read(1)
            if char == b'\n':
                stop = True
            else:
                bstr += char
        self._logger.setLevel(logging.DEBUG)
        self._logger.debug(
            'Readline: "%s"',
            bstr)
        return(bstr)

    outWaiting = out_waiting  # pyserial 2.7 / 3.0 compat.
