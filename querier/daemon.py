#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright© 2014 by Marc Culler and others.
# This code is adapted from daemon.py by Sander Marachal
# http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
# Copyright© 2003-2014 Stichting Lone Wolves
#
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

import sys, os, time, atexit, netifaces
from signal import SIGTERM 
from ConfigParser import ConfigParser
from . import Querier

config_file = '/etc/querierd'

class QuerierDaemon:
    """
    A daemon which sends IGMP queries at a specified interval
    (given in seconds).  The daemon supports the sysv-style start,
    stop and restart operations.  The process id is stored in the
    file specifed in the config_file by the pidfile line.
    """
    def __init__(self,
                 interval, source_address, pidfile,
                 stdin='/dev/null',
                 stdout='/dev/null',
                 stderr='/dev/null'):
        self.interval = float(interval)
        self.source_address = source_address
        self.pidfile = pidfile
        self.stdin, self.stdout, self.stderr = stdin, stdout, stderr
    
    def daemonize(self):
        """
        Do the UNIX double-fork magic, see Stevens' "Advanced 
        Programming in the UNIX Environment" for details
        (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError, e: 
            sys.stderr.write("fork #1 failed: %d (%s)\n" %
                             (e.errno, e.strerror))
            sys.exit(1)
    
        # decouple from parent environment
        os.chdir("/") 
        os.setsid() 
        os.umask(0) 
    
        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit from second parent
                sys.exit(0) 
        except OSError, e: 
            sys.stderr.write("fork #2 failed: %d (%s)\n" %
                             (e.errno, e.strerror))
            sys.exit(1) 
    
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
    
        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)
    
    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon is already running
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
    
        if pid:
            message = ("The file %s exists.\n"
                       "Is querierd already running?\n")
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        
        # Start the daemon
        self.daemonize()
        self.run()
        
    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
    
        if not pid:
            message = ("The pidfile %s does not exist."
                       "Was the querierd already stopped?\n")
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process    
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        Create a Querier and let it run.
        """
        print 'querier service starting. Using address %s'%ip
        Querier(self.source_address, self.interval).run()

if __name__ == "__main__":
    if os.getuid() != 0:
        print 'The querierd daemon must be controlled by root.'
        sys.exit(1)
                
    config = ConfigParser()
    config.read(config_file)
    pidfile = config.get('querierd', 'pidfile')
    query_interval = int(config.get('querierd', 'query_interval'))
    interface = config.get('querierd', 'interface')
    try:
        ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
    except ValueError:
        raise ValueError(
            'Interface %s not found. Please check %s .'%(interface, config_file)
        )
    daemon = QuerierDaemon(query_interval, ip, pidfile)
    
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print 'Querier daemon starting at %s.'%ip
            daemon.start()
        elif 'stop' == sys.argv[1]:
            print 'querierd stopping.'
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)

