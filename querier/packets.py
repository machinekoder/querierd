#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright© 2014 by Marc Culler and others.
# This file is part of QuerierD.
#
# QuerierD is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# QuerierD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with QuerierD.  If not, see <http://www.gnu.org/licenses/>.

import struct, socket, time

IGMP_type = {
    'query'    : 0x11,
    'v1_report': 0x12,
    'v2_report': 0x16,
    'v3_report': 0x22,
    'leave'    : 0x17}

class Packet(object):
    """
    Base class for internet packets.
    """
    _data = ''
    def __init__(self):
        self.format = '!'+''.join([self.formats[f]
                                   for f in self.fields])
        self.length = self.hdr_length = struct.calcsize(self.format)

    def __str__(self):
        self.compute_checksum()
        return self.header() + self._data

    def header(self):
        values = [getattr(self, field) for field in self.fields]
        return struct.pack(self.format, *values)

    def compute_checksum(self):
        self.checksum = 0
        values = [getattr(self, field) for field in self.fields]
        bytes = struct.pack(self.format, *values)
        shorts = struct.unpack('!%dH'%(self.hdr_length/2), bytes)
        S = sum(shorts)
        S = ((S >> 16) + (S & 0xffff))
        S += (S >> 16)
        self.checksum = S ^ 0xffff

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self, data):
        self._data = str(data)
        self.length = self.hdr_length + len(self._data)

class IGMPv2Packet(Packet):
    fields = ['_type', '_max_response_time', 'checksum', '_group']
    formats = {'_type':'B', '_max_response_time':'B', 'checksum':'H',
               '_group':'I'}
    _type = 0
    _max_response_time = 0
    checksum = 0
    _group = 0

    @property
    def type(self):
        return IGMP_type[self._type]
    @type.setter
    def type(self, typestr):
        self._type = IGMP_type[typestr]

    @property
    def max_response_time(self):
        return self._max_response_time
    @max_response_time.setter
    def max_response_time(self, units):
        # time units are 100 milliseconds, in exponential form if > 128
        self._max_response_time = units

    @property
    def group(self):
        return self._dst
    @group.setter
    def group(self, addr):
        self._group = struct.unpack("!I", socket.inet_aton(addr))[0]  

class IPv4Packet(Packet):
    fields = ['version_ihl', 'tos', 'length', '_id',
              'flags_offset', '_ttl', '_protocol', 'checksum',
              '_src', '_dst']
    formats = {'version_ihl':'B', 'tos':'B', 'length':'H',
               '_id':'H', 'flags_offset':'H', '_ttl':'B',
               '_protocol':'B', 'checksum':'H', '_src':'I', '_dst':'I'}
    version_ihl = 0x45
    tos = 0
    _id = 0
    flags_offset = 0
    _ttl = 64
    _protocol = 0 
    checksum = 0
    _src = 0
    _dst = 0

    @property
    def protocol(self):
        return self._protocol
    @protocol.setter
    def protocol(self, p):
        self._protocol = p

    @property
    def ttl(self):
        return self._ttl
    @protocol.setter
    def ttl(self, ttl_value):
        self._ttl = ttl_value

    @property
    def ident(self):
        return self._id
    @protocol.setter
    def ident(self, id_value):
        self._ttl = id_value

    @property
    def src(self):
        return self._src
    @protocol.setter
    def src(self, addr):
        self._src = struct.unpack("!I", socket.inet_aton(addr))[0]  

    @property
    def dst(self):
        return self._dst
    @protocol.setter
    def dst(self, addr):
        self._dst = struct.unpack("!I", socket.inet_aton(addr))[0]  
