#!/usr/bin/python
# Author: Prem Karat [prem.karat@gmail.com]
# MIT License
#
# Reference:
#   The daemonize() code is from python-cookbook3 by David Beazely


from fabric.api import env, run, get
from fabric.context_managers import hide
import atexit
import datetime
import os
import re
import sys
import signal
import socket
import tempfile
import time


# Globals
env.user = None
env.password = None
# or, specify path to server public key here:
# env.key_filename = ''
env.sudo_password = None
env.keepalive = 1
env.use_ssh_config = True
env.abort_on_prompts = True


def usage():
    print("Usage:")
    print("\t montior.py <host-ip> <interval> [start|stop]\n")
    print("\t <host-ip>: Valid IPv4 address")
    print("\t <interval>: in seconds. Minimum 1 sec")
    print("\t start: Run as daemon")
    print("\t stop: Stop daemon")


def getargs():
    if len(sys.argv) != 4:
        usage()
        raise SystemExit("Invalid Usage")

    ipaddr = sys.argv[1]
    interval = sys.argv[2]

    try:
        socket.inet_pton(socket.AF_INET, ipaddr)
    except socket.error:
        usage()
        raise SystemExit('Invalid IP address')

    try:
        interval = int(interval)
    except ValueError:
        usage()
        raise SystemExit('Invalid interval')

    if not interval:
        usage()
        raise SystemExit('Interval should be miminum 1 second')

    if sys.argv[3] != 'start' and sys.argv[3] != 'stop':
        usage()
        raise SystemExit('Unknown argument %s' % sys.argv[3])

    return (ipaddr, interval)


def daemonize(pidfile, stdin='/dev/null', stdout='/dev/null',
              stderr='/dev/null'):
    if os.path.exists(pidfile):
        raise RuntimeError('Already Running')
    try:
        if os.fork() > 0:
            raise SystemExit(0)
    except OSError:
        raise RuntimeError('fork 1 failed')

    os.umask(0)
    os.setsid()

    try:
        if os.fork() > 0:
            raise SystemExit(0)
    except OSError:
        raise RuntimeError('fork 2 failed')

    # Replace file descriptors for stdin, stdout, and stderr
    with open(stdin, 'rb', 0) as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open(stdout, 'ab', 0) as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
    with open(stderr, 'ab', 0) as f:
        os.dup2(f.fileno(), sys.stderr.fileno())

    # Write the PID file
    with open(pidfile, 'w') as f:
        f.write(str(os.getpid()))

    # Arrange to have the PID file removed on exit/signal
    atexit.register(lambda: os.remove(pidfile))

    # Signal handler for termination (required)
    def sigterm_handler(signo, frame):
        raise SystemExit(1)

    signal.signal(signal.SIGTERM, sigterm_handler)


def main(host, interval):
    env.host_string = host
    env.command_timeout = interval
    prev_nprocs = 0
    prev_dusage = 0
    filepos = 0
    PROCCMD = "sudo ps --no-headers -ef | wc -l"
    MEMCMD = "sudo ps --no-headers -eo pid,pmem,comm | sort -rk2 | head -n5"
    DISKCMD = "sudo df -h /var | tail -n1"
    SYSLOG = '/var/log/syslog'

    while True:
        with hide('running', 'stdout', 'stderr'):
            ts = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
            sys.stdout.write('%s\n' % ts)
            sys.stdout.write('-------------------\n')

            # Get # of process information
            output = run(PROCCMD)
            cur_nprocs = int(output.stdout)
            diff = cur_nprocs - prev_nprocs
            sys.stdout.write('Number of process: %s and %d\n'
                             % (cur_nprocs, diff))
            prev_nprocs = cur_nprocs

            # Get top 5 pmem process
            res = run(MEMCMD)
            sys.stdout.write('Top 5 process by memory usage:\t\n')
            for line in res.splitlines():
                sys.stdout.write('\t%s\n' % line.strip())

            # Get /var disk usage informatoin
            res = run(DISKCMD)
            match = re.findall('.*(\d+)%.*', res.stdout)
            if match:
                cur_dusage = int(match[0])
                diff = cur_dusage - prev_dusage
                sys.stdout.write('Disk space usage in /var partion: %s%% '
                                 'and %d%%\n' % (match[0], diff))
                prev_dusage = cur_dusage

            # Incremental check for ERROR (case insensitive) in syslog
            with tempfile.TemporaryFile() as f:
                get(SYSLOG, f)
                f.seek(filepos)
                for line in f:
                    if 'error' in line.lower():
                        sys.stdout.write('%s\n' % line.strip())
                filepos = f.tell()
                sys.stdout.write('\n')

            # Flush I/O buffers
            sys.stdout.flush()
            sys.stderr.flush()

            time.sleep(interval)


if __name__ == '__main__':
    PIDFILE = 'monitor.pid'
    ipaddr, interval = getargs()

    if sys.argv[3] == 'start':
        try:
            daemonize(PIDFILE, stdout='monitor.log',
                      stderr='monitor.log')
        except RuntimeError:
            raise SystemExit('Failed to run as daemon')

        main(ipaddr, interval)

    elif sys.argv[3] == 'stop':
        if os.path.exists(PIDFILE):
            with open(PIDFILE) as f:
                os.kill(int(f.read()), signal.SIGTERM)
        else:
            raise SystemExit('monitor daemon not running')
