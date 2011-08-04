# -*- coding: utf-8 -*-
"""
Simple ASCII time series format

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
from StringIO import StringIO
from obspy.core import Stream, Trace, UTCDateTime, Stats
from obspy.core.util import AttribDict
import numpy as np


HEADER = "TIMESERIES %s_%s_%s_%s_%s, %d samples, %d sps, %.26s, %s, %s, %s\n"


def isSLIST(filename):
    """
    Checks whether a file is ASCII SLIST format. Returns True or False.

    :type filename: string
    :param filename: Name of the ASCII SLIST file to be checked.
    :rtype: boolean
    :return: ``True`` if ASCII SLIST file.
    """
    try:
        temp = open(filename, 'rt').readline()
    except:
        return False
    if not temp.startswith('TIMESERIES'):
        return False
    if not 'SLIST' in temp:
        return False
    return True


def isTSPAIR(filename):
    """
    Checks whether a file is ASCII TSPAIR format. Returns True or False.

    :type filename: string
    :param filename: Name of the ASCII TSPAIR file to be checked.
    :rtype: boolean
    :return: ``True`` if ASCII TSPAIR file.
    """
    try:
        temp = open(filename, 'rt').readline()
    except:
        return False
    if not temp.startswith('TIMESERIES'):
        return False
    if not 'TSPAIR' in temp:
        return False
    return True


def readSLIST(filename, headonly=False):
    """
    Reads a ASCII SLIST file and returns an ObsPy Stream object.

    .. note::
        This function should NOT be called directly, it registers via the
        ObsPy :func:`~obspy.core.stream.read` function, call this instead.

    :type filename: string
    :param filename: ASCII file to be read.
    :type headonly: bool, optional
    :param headonly: If set to True, read only the head. This is most useful
        for scanning available data in huge (temporary) data sets.
    :rtype: :class:`~obspy.core.stream.Stream`
    :return: A ObsPy Stream object.

    >>> from obspy.core import read
    >>> st = read('/path/to/slist.ascii')
    """
    fh = open(filename, 'rt')
    # read file and split text into channels
    headers = {}
    key = None
    for line in fh.xreadlines():
        if line.isspace():
            # blank line
            continue
        elif line.startswith('TIMESERIES'):
            # new header line
            key = line
            headers[key] = StringIO()
        elif headonly:
            # skip data for option headonly
            continue
        elif key:
            # data entry - may be written in multiple columns
            headers[key].write(line.strip() + ' ')
    fh.close()
    # create ObsPy stream object
    stream = Stream()
    for header, data in headers.iteritems():
        # create Stats
        stats = Stats()
        parts = header.replace(',', '').split()
        temp = parts[1].split('_')
        stats.network = temp[0]
        stats.station = temp[1]
        stats.location = temp[2]
        stats.channel = temp[3]
        stats.sampling_rate = parts[4]
        # quality only used in MSEED
        stats.mseed = AttribDict({'dataquality' : temp[4]})
        stats.ascii = AttribDict({'unit' : parts[-1]})
        stats.starttime = UTCDateTime(parts[6])
        stats.npts = parts[2]
        if headonly:
            # skip data
            stream.append(Trace(header=stats))
        else:
            # parse data
            data.seek(0)
            if parts[8] == 'INTEGER':
                data = np.loadtxt(data, dtype='int')
            elif parts[8] == 'FLOAT':
                data = np.loadtxt(data, dtype='float32')
            else:
                raise NotImplementedError
            stream.append(Trace(data=data, header=stats))
    return stream


def readTSPAIR(filename, headonly=False):
    """
    Reads a ASCII TSPAIR file and returns an ObsPy Stream object.

    .. note::
        This function should NOT be called directly, it registers via the
        ObsPy :func:`~obspy.core.stream.read` function, call this instead.

    :type filename: string
    :param filename: ASCII file to be read.
    :type headonly: bool, optional
    :param headonly: If set to True, read only the headers. This is most useful
        for scanning available data in huge (temporary) data sets.
    :rtype: :class:`~obspy.core.stream.Stream`
    :return: A ObsPy Stream object.

    >>> from obspy.core import read
    >>> st = read('/path/to/tspair.ascii')
    """
    fh = open(filename, 'rt')
    # read file and split text into channels
    headers = {}
    key = None
    for line in fh.xreadlines():
        if line.isspace():
            # blank line
            continue
        elif line.startswith('TIMESERIES'):
            # new header line
            key = line
            headers[key] = StringIO()
        elif headonly:
            # skip data for option headonly
            continue
        elif key:
            # data entry - may be written in multiple columns
            headers[key].write(line.strip().split()[-1] + ' ')
    fh.close()
    # create ObsPy stream object
    stream = Stream()
    for header, data in headers.iteritems():
        # create Stats
        stats = Stats()
        parts = header.replace(',', '').split()
        temp = parts[1].split('_')
        stats.network = temp[0]
        stats.station = temp[1]
        stats.location = temp[2]
        stats.channel = temp[3]
        stats.sampling_rate = parts[4]
        # quality only used in MSEED
        stats.mseed = AttribDict({'dataquality' : temp[4]})
        stats.ascii = AttribDict({'unit' : parts[-1]})
        stats.starttime = UTCDateTime(parts[6])
        stats.npts = parts[2]
        if headonly:
            # skip data
            stream.append(Trace(header=stats))
        else:
            # parse data
            data.seek(0)
            if parts[8] == 'INTEGER':
                data = np.loadtxt(data, dtype='int')
            elif parts[8] == 'FLOAT':
                data = np.loadtxt(data, dtype='float32')
            else:
                raise NotImplementedError
            stream.append(Trace(data=data, header=stats))
    return stream


def writeSLIST(stream, filename, **kwargs):
    """
    Writes a ASCII SLIST file.

    .. note::
        This function should NOT be called directly, it registers via the
        :meth:`~obspy.core.stream.Stream.write` method of an ObsPy
        :class:`~obspy.core.stream.Stream` object, call this instead.

    :type filename: stream : :class:`~obspy.core.stream.Stream`
    :param filename: The ObsPy Stream object to write.
    :type filename: string
    :param filename: Name of file to write.

    .. rubric:: SLIST Format Description

    SLIST is a simple ASCII time series format. Each contiguous time series
    segment (no gaps or overlaps) is represented with a header line followed by
    a sample lists. There are no restrictions on how the segments are organized
    into files, a file might contain a single segment or many, concatenated
    segments either for the same channel or many different channels.

    Header lines have the general form::

        TIMESERIES SourceName, # samples, # sps, Time, Format, Type, Units

    with

    ``SourceName``
        "Net_Sta_Loc_Chan_Qual", no spaces, quality code optional
    ``# samples``
        Number of samples following header
    ``# sps``
        Sampling rate in samples per second
    ``Time``
        Time of first sample in ISO YYYY-MM-DDTHH:MM:SS.FFFFFF format
    ``Format``
        'TSPAIR' (fixed)
    ``Type``
        Sample type 'INTEGER', 'FLOAT' or 'ASCII'
    ``Units``
        Units of time-series, e.g. Counts, M/S, etc., may not contain
        spaces

    Samples are listed in 6 columns with the time-series incrementing from left
    to right and wrapping to the next line. The time of the first sample is the
    time listed in the header.

    *Example SLIST file*::

        TIMESERIES NL_HGN_00_BHZ_R, 12 samples, 40 sps, 2003-05-29T02:13:22.043400, SLIST, INTEGER, Counts
        2787        2776        2774        2780        2783        2782
        2776        2766        2759        2760        2765        2767
        ...
    """
    fh = open(filename, 'wt')
    for trace in stream:
        stats = trace.stats
        # quality code
        try:
            dataquality = stats.mseed.dataquality
        except:
            dataquality = ''
        # sample type
        if trace.data.dtype.name.startswith('int'):
            dtype = 'INTEGER'
        elif trace.data.dtype.name.startswith('float'):
            dtype = 'FLOAT'
        else:
            raise NotImplementedError
        # unit
        try:
            unit = stats.ascii.unit
        except:
            unit = ''
        # write trace header
        header = HEADER % (stats.network, stats.station, stats.location,
                           stats.channel, dataquality, stats.npts,
                           stats.sampling_rate, stats.starttime, 'SLIST',
                           dtype, unit)
        fh.write(header)
        # write data
        rest = stats.npts % 5
        if rest:
            data = trace.data[:-rest]
        else:
            data = trace.data
        data = data.reshape((-1, 5))
        for slice in data:
            np.savetxt(fh, slice, fmt="%f")
        if rest:
            np.savetxt(fh, trace.data[-rest:], fmt="%f")
    fh.close()


def writeTSPAIR(stream, filename, **kwargs):
    """
    Writes a ASCII TSPAIR file.

    .. note::
        This function should NOT be called directly, it registers via the
        :meth:`~obspy.core.stream.Stream.write` method of an ObsPy
        :class:`~obspy.core.stream.Stream` object, call this instead.

    :type filename: stream : :class:`~obspy.core.stream.Stream`
    :param filename: The ObsPy Stream object to write.
    :type filename: string
    :param filename: Name of file to write.

    .. rubric:: TSPAIR Format Description

    TSPAIR is a simple ASCII time series format. Each contiguous time series
    segment (no gaps or overlaps) is represented with a header line followed by
    data samples in time-sample pairs. There are no restrictions on how the
    segments are organized into files, a file might contain a single segment
    or many, concatenated segments either for the same channel or many
    different channels.

    Header lines have the general form::

        TIMESERIES SourceName, # samples, # sps, Time, Format, Type, Units

    with

    ``SourceName``
        "Net_Sta_Loc_Chan_Qual", no spaces, quality code optional
    ``# samples``
        Number of samples following header
    ``# sps``
        Sampling rate in samples per second
    ``Time``
        Time of first sample in ISO YYYY-MM-DDTHH:MM:SS.FFFFFF format
    ``Format``
        'TSPAIR' (fixed)
    ``Type``
        Sample type 'INTEGER', 'FLOAT' or 'ASCII'
    ``Units``
        Units of time-series, e.g. Counts, M/S, etc., may not contain
        spaces

    *Example TSPAIR file*::

        TIMESERIES NL_HGN_00_BHZ_R, 12 samples, 40 sps, 2003-05-29T02:13:22.043400, TSPAIR, INTEGER, Counts
        2003-05-29T02:13:22.043400  2787
        2003-05-29T02:13:22.068400  2776
        2003-05-29T02:13:22.093400  2774
        2003-05-29T02:13:22.118400  2780
        2003-05-29T02:13:22.143400  2783
        2003-05-29T02:13:22.168400  2782
        2003-05-29T02:13:22.193400  2776
        2003-05-29T02:13:22.218400  2766
        2003-05-29T02:13:22.243400  2759
        2003-05-29T02:13:22.268400  2760
        2003-05-29T02:13:22.293400  2765
        2003-05-29T02:13:22.318400  2767
        ...
    """
    fh = open(filename, 'wt')
    for trace in stream:
        stats = trace.stats
        # quality code
        try:
            dataquality = stats.mseed.dataquality
        except:
            dataquality = ''
        # sample type
        if trace.data.dtype.name.startswith('int'):
            dtype = 'INTEGER'
        elif trace.data.dtype.name.startswith('float'):
            dtype = 'FLOAT'
        else:
            raise NotImplementedError
        # unit
        try:
            unit = stats.ascii.unit
        except:
            unit = ''
        # write trace header
        header = HEADER % (stats.network, stats.station, stats.location,
                           stats.channel, dataquality, stats.npts,
                           stats.sampling_rate, stats.starttime, 'TSPAIR',
                           dtype, unit)
        fh.write(header)
        # write data
        times = np.arange(stats.starttime,
                          stats.endtime + stats.delta,
                          stats.delta)
        data = np.vstack((times, trace.data)).T
        # .26s cuts the Z from the time string
        np.savetxt(fh, data, fmt="%.26s  %f")
    fh.close()


if __name__ == '__main__': # pragma: no cover
    import doctest
    doctest.testmod(exclude_empty=True)
