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

import os, netifaces
from ConfigParser import ConfigParser
from . import Querier

config_file = '/etc/querierd'

def main():
    if os.getuid() != 0:
        print 'You must be root to run a querier.'
        sys.exit(1)

    config = ConfigParser()
    config.read(config_file)
    query_interval = int(config.get('querierd', 'query_interval'))
    interface = config.get('querierd', 'interface')
    try:
        ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
    except ValueError:
        raise ValueError(
            'Interface %s not found. Please check %s .'%(interface, config_file)
        )
    print 'querier service starting. Using address %s'%ip
    Querier(ip, query_interval).run()

if __name__ == "__main__":
    main()

