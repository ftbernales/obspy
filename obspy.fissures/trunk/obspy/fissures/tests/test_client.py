#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
The DHI/Fissures client test suite.
"""

from obspy.core import UTCDateTime
from obspy.fissures import Client
import inspect
import numpy as np
import os
import unittest


class ClientTestSuite(unittest.TestCase):
    """
    Test cases for DHI/Fissures client
    """
    def setUp(self):
        self.client = Client()
        pass

    def tearDown(self):
        pass

    def test_client(self):
        """
        Retrieve data from DHI/Fissures, compare stat attributes.
        
        """
        t = UTCDateTime("2003-06-20T05:59:00.0000")
        st = self.client.getWaveForm("GE", "APE", "", "SHZ", t, t+600)
        tr = st[0]
        self.assertEqual('GE', tr.stats.network)
        self.assertEqual('APE', tr.stats.station)
        self.assertEqual('', tr.stats.location)
        self.assertEqual('SHZ', tr.stats.channel)
        self.assertEqual(UTCDateTime(2003, 6, 20, 5, 57, 43, 321000), tr.stats.starttime)
        self.assertEqual(50.0, tr.stats.sampling_rate)
        #XXX: Do not check values of data-samples. Compare to ArcLink/SOD
        self.assertEqual(37364, len(tr.data))


def suite():
    return unittest.makeSuite(ClientTestSuite, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
