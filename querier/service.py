#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright© 2016 by Alexander Roessler.
# Based on the work of Mark Culler and others.
# This file is part of QuerierD.
#
# QuerierD is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# QuerierD is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with QuerierD.  If not, see <http://www.gnu.org/licenses/>.

from . import Querier
import threading
import time
import sys
import argparse
import os
from netifaces import interfaces, ifaddresses, AF_INET


class QuerierInstance:
    def __init__(self, address, interval):
        self.address = address
        self.interval = interval
        self.querier = Querier(address, interval)
        self.thread = thread = threading.Thread(target=self.run)
        thread.start()

    def run(self):
        self.querier.run()

    def stop(self):
        self.querier.stop.set()


def ip4_addresses():
    ip_list = []
    for interface in interfaces():
        if interface == 'lo':
            continue
        addresses = ifaddresses(interface)
        if AF_INET in addresses:
            for link in addresses[AF_INET]:
                ip_list.append(link['addr'])
    return ip_list


def main():
    parser = argparse.ArgumentParser(description='Querierd queries the multicast group in a certain interval to prevent IGMP snooping')
    parser.add_argument('-i', '--interval', help='IGMP query interval', default=60.0)
    parser.add_argument('-d', '--debug', help='Enable debug mode', action='store_true')
    args = parser.parse_args()

    if os.getuid() != 0:
        print 'You must be root to run a querier.'
        sys.exit(1)

    debug = args.debug
    interval = args.interval
    wait = 5.0  # network interface checking interval
    processes = {}

    try:
        while True:
            addresses = ip4_addresses()
            for address in addresses:
                if address not in processes:
                    if debug:
                        print('adding new querier: %s' % address)
                    processes[address] = QuerierInstance(address, interval)

            removed = []
            for proc in processes:
                if proc not in addresses:
                    if debug:
                        print('stopping querier: %s' % proc)
                    processes[proc].stop()
                    removed.append(proc)
            for proc in removed:
                processes.pop(proc)

            time.sleep(wait)
    except KeyboardInterrupt:
        pass

    if debug:
        print("stopping threads")
    for proc in processes:
        processes[proc].stop()

    # wait for all threads to terminate
    while threading.active_count() > 1:  # one thread for every process is left
        time.sleep(0.1)

    if debug:
        print("threads stopped")
    sys.exit(0)

if __name__ == "__main__":
    main()
