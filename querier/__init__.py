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

import socket, time, os
from .packets import IPv4Packet, IGMPv2Packet

version = '0.1'
__all__ = ['Querier']

all_routers = '224.0.0.1'
mdns_group = '224.0.0.251'

class Querier:
    """
    Sends an IGMP query packet at a specified time interval (in seconds).
    """
    def __init__(self, source_address, interval):
        if os.getuid() != 0:
            raise RuntimeError('You must be root to create a Querier.')
        self.source_address = source_address
        self.interval = interval
        self.socket = sock = socket.socket(socket.AF_INET,
                                           socket.SOCK_RAW,
                                           socket.IPPROTO_RAW)
        time.sleep(1) # Can't set options too soon (???)
        sock.settimeout(5)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        sock.bind((source_address,0))
        self.build_query_packet()
        
    def build_query_packet(self):
        igmp = IGMPv2Packet()
        igmp.type = 'query'
        #max_response_time should be 0 for a v1 query
        #igmp.max_response_time = 100

        self.packet = ip = IPv4Packet()
        ip.protocol = socket.IPPROTO_IGMP
        ip.ttl = 1
        ip.src = self.source_address
        ip.dst = all_routers
        ip.data = igmp
    
    def run(self):
        while True:
            self.socket.sendto(str(self.packet), (all_routers, 0))
            time.sleep(self.interval)

