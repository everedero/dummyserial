#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Dummy Serial Lookup Function Definitions"""

import logging

def default(in_str, ans_when_invalid):
    """
    Default dummy. Echoes input and answer invalid when
    no string is input.
    """
    logging.warning("I am a bogus look-up function, please vverride me!")
    if len(in_str) == 0:
        return(ans_when_invalid)
    return(in_str)
